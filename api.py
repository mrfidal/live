import asyncio
import os
import platform
import websockets
import json
from websockets.server import serve

if platform.system() == "Windows":
    from winpty import PtyProcess
else:
    import ptyprocess

class TerminalServer:
    def __init__(self):
        self.pty_process = None
        self.websocket = None
        
    def create_pty(self, cols=120, rows=30):
        """Create a new pseudo-terminal session"""
        shell = "powershell.exe" if platform.system() == "Windows" else "bash"
        
        if platform.system() == "Windows":
            # Windows with winpty
            self.pty_process = PtyProcess.spawn(
                shell,
                dimensions=(rows, cols),
                cwd=os.path.expanduser("~"),
                env=os.environ.copy()
            )
        else:
            self.pty_process = ptyprocess.PtyProcessUnicode.spawn(
                [shell],
                dimensions=(rows, cols),
                cwd=os.path.expanduser("~"),
                env=os.environ.copy()
            )
        
        return self.pty_process
    
    async def handle_connection(self, websocket):
        print("Client connected")
        

        self.websocket = websocket
        

        self.create_pty()
        

        read_task = asyncio.create_task(self.read_from_pty())
        
        try:

            async for message in websocket:
                data = json.loads(message)
                
                if data['type'] == 'terminal:write':

                    self.pty_process.write(data['data'])
                    
                elif data['type'] == 'terminal:resize':

                    cols = data.get('cols', 120)
                    rows = data.get('rows', 30)
                    if platform.system() == "Windows":
                        self.pty_process.set_console_size(cols, rows)
                    else:
                        self.pty_process.setwinsize(rows, cols)
                        
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        finally:

            read_task.cancel()
            if self.pty_process:
                self.pty_process.terminate()
    
    async def read_from_pty(self):
        while True:
            try:
                if platform.system() == "Windows":

                    data = self.pty_process.read(4096)
                    if data:
                        await self.websocket.send(json.dumps({
                            'type': 'terminal:data',
                            'data': data
                        }))
                else:
                    # Unix ptyprocess reading
                    try:
                        data = self.pty_process.read(4096)
                        if data:
                            await self.websocket.send(json.dumps({
                                'type': 'terminal:data',
                                'data': data
                            }))
                    except ptyprocess.EOF:
                        break
                
                await asyncio.sleep(0.01) 
                
            except Exception as e:
                print(f"Error reading from PTY: {e}")
                break


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

terminal_sessions = {}

@app.get("/")
async def root():
    return {"message": "Terminal backend running"}

@app.websocket("/terminal")
async def terminal_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Create terminal session for this connection
    shell = "powershell.exe" if platform.system() == "Windows" else "bash"
    
    if platform.system() == "Windows":
        from winpty import PtyProcess
        pty_process = PtyProcess.spawn(
            shell,
            dimensions=(30, 120),
            cwd=os.path.expanduser("~"),
            env=os.environ.copy()
        )
    else:
        import ptyprocess
        pty_process = ptyprocess.PtyProcessUnicode.spawn(
            [shell],
            dimensions=(30, 120),
            cwd=os.path.expanduser("~"),
            env=os.environ.copy()
        )
    
    async def read_from_pty():
        """Read from PTY and send to WebSocket"""
        while True:
            try:
                if platform.system() == "Windows":
                    data = pty_process.read(4096)
                    if data:
                        await websocket.send_text(json.dumps({
                            'type': 'terminal:data',
                            'data': data
                        }))
                else:
                    try:
                        data = pty_process.read(4096)
                        if data:
                            await websocket.send_text(json.dumps({
                                'type': 'terminal:data',
                                'data': data
                            }))
                    except ptyprocess.EOF:
                        break
                
                await asyncio.sleep(0.01)
                
            except Exception as e:
                print(f"PTY read error: {e}")
                break
    

    read_task = asyncio.create_task(read_from_pty())
    
    try:

        async for message in websocket.iter_text():
            data = json.loads(message)
            
            if data['type'] == 'terminal:write':
                pty_process.write(data['data'])
            elif data['type'] == 'terminal:resize':
                cols = data.get('cols', 120)
                rows = data.get('rows', 30)
                if platform.system() == "Windows":
                    pty_process.set_console_size(cols, rows)
                else:
                    pty_process.setwinsize(rows, cols)
                    
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        read_task.cancel()
        pty_process.terminate()

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    print(f"Server running on port {PORT}")

    uvicorn.run(app, host="0.0.0.0", port=PORT)
