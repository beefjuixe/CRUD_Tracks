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
            #print("Parsed model:", parsed)
            data.append(parsed)
    yield

app = FastAPI(lifespan=lifespan)
@app.get('/tracks/', response_model= List[Track])
def track():
    return data

@app.get('/tracks/{track_id}' , response_model = Union[Track,str])
def get_track(track_id: int, response: Response):
    track = None
    for t in data:
        if t.id == track_id:
            track = t
            break
    if track is None:
        response.status_code = 404
        return "Track not found"
    return track

@app.post('/tracks/',response_model = Track, status_code = 201)
def create_track(track: Track):
    track_dict = track.model_dump()
    track_dict['id'] = max((t.id for t in data), default=0) + 1
    new_track = Track(**track_dict)
    data.append(new_track)
    return new_track

@app.put('/tracks/{track_id}' , response_model = Union[Track,str])
def edit_track(track_id: int, updated_track: Track, response: Response):
    track = None
    for t in data:
        if t.id == track_id:
            track = t
            break
    if track is None:
        response.status_code = 404
        return "Track not found"
    
    for key, val in updated_track.model_dump().items():
        if key != 'id':
            setattr(track, key, val)
    return track

@app.delete('/tracks/{track_id}')
def delete_track(track_id: int, response: Response):
    track_index = None
    for i,t in enumerate(data):
        if t.id == track_id:
            track_index = i
            break
    if track_index is None:
        response.status_code = 404
        return "Track not found"
    data.pop(track_index)
    return Response(status_code=200)