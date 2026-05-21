from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import time

app = FastAPI(title="Aura Player Backend")

# Allow Lovable frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

download_queue = {}

class DownloadRequest(BaseModel):
    track_id: str
    title: str
    artist: str

def process_soulseek_download(track_id: str, title: str, artist: str):
    print(f"Starting search for: {artist} - {title}")
    download_queue[track_id]["status"] = "downloading"
    
    # Simulate download progress for testing the UI
    for i in range(1, 11):
        time.sleep(1)
        download_queue[track_id]["progress"] = i * 10
        print(f"[{title}] Progress: {i * 10}%")
        
    download_queue[track_id]["status"] = "completed"
    print(f"Finished downloading: {title}")

@app.post("/api/downloads")
async def request_download(req: DownloadRequest, background_tasks: BackgroundTasks):
    download_queue[req.track_id] = {
        "track_id": req.track_id,
        "title": req.title,
        "artist": req.artist,
        "status": "pending",
        "progress": 0.0
    }
    background_tasks.add_task(process_soulseek_download, req.track_id, req.title, req.artist)
    return {"message": "Download added to queue"}

@app.get("/api/downloads")
async def get_downloads():
    return list(download_queue.values())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5030)
