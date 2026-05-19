import asyncio
import os
import pty
import select
import signal
import struct
import termios
import fcntl
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TerminalSession:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.pid = None
        self.master_fd = None
        
    def create_process(self, cols: int = 120, rows: int = 30):
        shell = os.environ.get('SHELL', '/bin/bash')
        
        master_fd, slave_fd = pty.openpty()
        
        self.pid = os.fork()
        
        if self.pid == 0:
            try:
                os.setsid()
                
                winsize = struct.pack('HHHH', rows, cols, 0, 0)
                termios.tcsetwinsize(slave_fd, termios.TCSANOW, winsize)
                
                os.dup2(slave_fd, 0)
                os.dup2(slave_fd, 1)
                os.dup2(slave_fd, 2)
                
                os.close(master_fd)
                
                os.execvp(shell, [shell])
            except Exception as e:
                print(f"Error: {e}")
                os._exit(1)
        else:
            os.close(slave_fd)
            self.master_fd = master_fd
            
            fl = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
            fcntl.fcntl(self.master_fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
    def write(self, data: str):
        try:
            os.write(self.master_fd, data.encode())
        except Exception as e:
            print(f"Write error: {e}")
    
    def terminate(self):
        try:
            os.kill(self.pid, signal.SIGTERM)
            os.close(self.master_fd)
        except Exception:
            pass
    
    def resize(self, cols: int, rows: int):
        try:
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            termios.tcsetwinsize(self.master_fd, termios.TCSANOW, winsize)
        except Exception:
            pass
    
    async def read_output(self):
        buffer = ""
        while True:
            try:
                rlist, _, _ = select.select([self.master_fd], [], [], 0.1)
                if self.master_fd in rlist:
                    try:
                        data = os.read(self.master_fd, 4096)
                        if data:
                            decoded = data.decode('utf-8', errors='ignore')
                            buffer += decoded
                            
                            if '\n' in buffer:
                                lines = buffer.split('\n')
                                buffer = lines[-1]
                                for line in lines[:-1]:
                                    if line.strip() or line == '':
                                        await self.websocket.send_text(json.dumps({
                                            'type': 'terminal:data',
                                            'data': line + '\n'
                                        }))
                    except BlockingIOError:
                        pass
                    except OSError:
                        break
                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"Read error: {e}")
                break

@app.websocket("/terminal")
async def terminal_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    session = TerminalSession(websocket)
    session.create_process()
    
    read_task = asyncio.create_task(session.read_output())
    
    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            
            if data['type'] == 'terminal:write':
                session.write(data['data'])
            elif data['type'] == 'terminal:resize':
                session.resize(data.get('cols', 120), data.get('rows', 30))
                
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        read_task.cancel()
        session.terminate()

@app.get("/")
async def root():
    return {"status": "Terminal backend running"}

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    print(f"Server running on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
