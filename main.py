import os
import asyncio
import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Query
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Client:
    def __init__(self, ws: WebSocket, name: str):
        self.ws = ws
        self.name = name

clients: list[Client] = []

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket, name: str = Query("Guest")):
    await websocket.accept()
    client = Client(websocket, name.strip() or "Guest")
    clients.append(client)
    try:
        while True:
            text = await websocket.receive_text()
            payload = f"{client.name}: {text}"
            await asyncio.gather(*[
                c.ws.send_text(payload) for c in clients if c is not client
            ])
    except WebSocketDisconnect:
        clients.remove(client)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8001)))
