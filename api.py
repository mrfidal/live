import asyncio
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import ptyprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/terminal")
async def terminal_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    shell = os.environ.get('SHELL', '/bin/bash')
    
    pty_process = ptyprocess.PtyProcessUnicode.spawn(
        [shell],
        dimensions=(30, 120),
        cwd=os.path.expanduser("~"),
        env=os.environ.copy()
    )
    
    async def read_output():
        while True:
            try:
                data = pty_process.read(4096)
                if data:
                    await websocket.send_text(json.dumps({
                        'type': 'terminal:data',
                        'data': data
                    }))
                await asyncio.sleep(0.01)
            except ptyprocess.EOF:
                break
            except Exception as e:
                print(f"Read error: {e}")
                break
    
    read_task = asyncio.create_task(read_output())
    
    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            
            if data['type'] == 'terminal:write':
                pty_process.write(data['data'])
            elif data['type'] == 'terminal:resize':
                pty_process.setwinsize(data.get('rows', 30), data.get('cols', 120))
                
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        read_task.cancel()
        pty_process.terminate()

@app.get("/")
async def root():
    return {"status": "Terminal backend running"}

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    print(f"Server running on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)


# pip install fastapi uvicorn ptyprocess
