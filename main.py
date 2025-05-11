import json
import pathlib
from typing import List,Union,Dict
from fastapi import FastAPI, Response
from models import Track
from contextlib import asynccontextmanager


data = []
@asynccontextmanager
async def lifespan(app: FastAPI):
    datapath = pathlib.Path(__file__).parent / 'data' / 'tracks.json'
    print("Resolved path:", datapath.resolve())
    with open(datapath, 'r') as f:
        tracks = json.load(f)
        for track in tracks:
            parsed = Track(**track)
            print("Parsed model:", parsed)
            data.append(parsed)
    yield

app = FastAPI(lifespan=lifespan)
@app.get('/tracks/', response_model= List[Track])
def track():
    return data

@app.get('/tracks/{track_id}' , response_model = Union[Track,str])
def track(track_id: int, response: Response):
    track = None
    for t in data:
        if t.id == track_id:
            track = t
            break
    if track is None:
        response.status_code = 404
        return "Track not found"
    return track
