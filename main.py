from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import whisper
from pydantic import BaseModel
import hashlib
from pathlib import Path
import json
import os
from utils.mongo import insert, retrieve
from fastapi.encoders import jsonable_encoder
app = FastAPI()
model = whisper.load_model("tiny")

class AudioTranscriptModel(BaseModel):
    path: str
    file_id: int
    

@app.post("/transcript")
async def sample(data: AudioTranscriptModel, background_tasks: BackgroundTasks):
    hash = hashlib.md5(open(data.path, "rb").read()).hexdigest()
    cache_path = "{}/cache/{}.bin".format(Path().absolute(), hash)

    def process_audio():
        result = model.transcribe(data.path)
        with open(cache_path, 'w') as f:
            f.write(json.dumps(result))
        insert(result, data.file_id) 
        
    if os.path.exists(cache_path):
        result = json.loads(open(cache_path, encoding="utf8", errors='ignore').read())
    else:
     # Insert the result into MongoDB
        background_tasks.add_task(process_audio)
        result = {}
    # flags = get_flags(result['text'])
    return {
        "status": "file transcript requested!", 
        "transcript": result
    }
    
@app.get("/transcript/{file_id}")
async def get_text(file_id: str):
    try:
        
        file_id = int(file_id)   
    except ValueError:
        pass
    
    try:
        
        result = retrieve(file_id=file_id)
        if result:
            # convert objectid to string for JSON serialization
            result['_id'] = str(result['_id'])
            return JSONResponse(content=jsonable_encoder(result))
        else:
            raise HTTPException(status_code=404, details="transcript not found!")
    except Exception as e:
        raise HTTPException(status_code=500, details=str(e))    