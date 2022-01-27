import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="⚡ FASTAPI", description="Live demo song api", version="1.0.0")


class Album(BaseModel):
    id: str
    name: str
    release: datetime


class Song(BaseModel):
    id: str
    name: str
    duration: int
    album: Album


class CreateSong(BaseModel):
    name: str
    duration: int


class UpdateSong(CreateSong):
    name: Optional[str]
    duration: Optional[int]


album = Album(
    id=uuid.uuid4().hex,
    name="Uke greatest hits",
    release=datetime.utcnow()
)

song_database: List[Song] = [
    Song(id=uuid.uuid4().hex, name="Tetris Theme", duration=60, album=album),
    Song(id=uuid.uuid4().hex, name="Turrican 2 Theme", duration=30, album=album)
]


async def get_song_by_id_or_exception(id: str) -> Song:
    if (song := next(filter(lambda x: x.id == id, song_database), None)) is None:
        raise HTTPException(status_code=404, detail="song not found")
    return song


@app.get(path="/songs")
async def get_song(id: str = None):
    if not id:
        return song_database
    return await get_song_by_id_or_exception(id)


@app.post(path="/songs", response_model=Song)
async def create_song(data: CreateSong):
    song = Song(id=uuid.uuid4().hex, album=album, **data.dict())
    song_database.append(song)
    return song


@app.patch(path="/songs/{id}", response_model=Song)
async def update_song(id: str, data: UpdateSong):
    song: Song = await get_song_by_id_or_exception(id)

    index = song_database.index(song)

    new_song = song_database[index].copy(update=data.dict(exclude_none=True))
    song_database[index] = new_song
    return new_song


@app.delete(path="/songs/{id}", response_model=Song)
async def delete_song(id: str):
    song: Song = await get_song_by_id_or_exception(id)
    index = song_database.index(song)
    song_database.pop(index)
    return song
