from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import time
import requests
import asyncio
import os

app = FastAPI(title="Aura Player Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

download_queue = {}
SLSKD_API_URL = "http://localhost:50300/api/v0"

class DownloadRequest(BaseModel):
    track_id: str
    title: str
    artist: str

def process_soulseek_download(track_id: str, title: str, artist: str):
    print(f"Starting real Soulseek search for: {artist} - {title}")
    download_queue[track_id]["status"] = "downloading"
    download_queue[track_id]["progress"] = 10

    search_query = f"{artist} {title} flac"
    
    try:
        search_payload = {
            "id": track_id,
            "searchText": search_query,
            "searchTimeout": 10000,
            "filterResponses": True
        }
        
        response = requests.post(f"{SLSKD_API_URL}/searches", json=search_payload)
        
        if response.status_code == 200:
            print(f"Search initiated successfully in slskd for: {search_query}")
            download_queue[track_id]["progress"] = 30
            
            time.sleep(10)
            
            results_res = requests.get(f"{SLSKD_API_URL}/searches/{track_id}")
            if results_res.status_code == 200:
                search_data = results_res.json()
                files_found = len(search_data.get('responses', []))
                print(f"✅ Found {files_found} users sharing this track!")
                
                download_queue[track_id]["progress"] = 100
                download_queue[track_id]["status"] = "completed"
            else:
                download_queue[track_id]["status"] = "error"
        else:
            print("Failed to start search with slskd")
            download_queue[track_id]["status"] = "error"
            
    except Exception as e:
        print(f"Error communicating with slskd: {e}")
        download_queue[track_id]["status"] = "error"

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
    # Dynamically grab the port Render wants us to use, or fallback to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
