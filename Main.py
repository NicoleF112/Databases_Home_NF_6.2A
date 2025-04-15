from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import motor.motor_asyncio
import base64
from bson import ObjectId

app = FastAPI()

# Connect to Mongo Atlas
MONGO_URL = "mongodb+srv://admin:123@databaseessensials62a.fqeq1cm.mongodb.net/"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["DatabaseEssensials62A"]  # Make sure the DB name matches Atlas exactly

class PlayerScore(BaseModel):
    player_name: str
    score: int

# ----------------------------- UPLOAD ROUTES -----------------------------

@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    content = await file.read()
    encoded = base64.b64encode(content).decode("utf-8")
    sprite_doc = {
        "filename": file.filename,
        "content_base64": encoded,
        "content_type": file.content_type
    }
    result = await db.sprites.insert_one(sprite_doc)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    content = await file.read()
    encoded = base64.b64encode(content).decode("utf-8")
    audio_doc = {
        "filename": file.filename,
        "content_base64": encoded,
        "content_type": file.content_type
    }
    result = await db.audio.insert_one(audio_doc)
    return {"message": "Audio uploaded", "id": str(result.inserted_id)}

@app.post("/player_score")
async def add_score(score: PlayerScore):
    result = await db.scores.insert_one(score.dict())
    return {"message": "Score recorded", "id": str(result.inserted_id)}

# ----------------------------- RETRIEVAL ROUTES -----------------------------

@app.get("/get_sprite/{sprite_id}")
async def get_sprite(sprite_id: str):
    sprite = await db.sprites.find_one({"_id": ObjectId(sprite_id)})
    if not sprite:
        raise HTTPException(status_code=404, detail="Sprite not found")
    return sprite

@app.get("/get_audio/{audio_id}")
async def get_audio(audio_id: str):
    audio = await db.audio.find_one({"_id": ObjectId(audio_id)})
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    return audio

@app.get("/get_score/{score_id}")
async def get_score(score_id: str):
    score = await db.scores.find_one({"_id": ObjectId(score_id)})
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    return score

# ----------------------------- UPDATE ROUTES -----------------------------

@app.put("/update_sprite/{sprite_id}")
async def update_sprite(sprite_id: str, file: UploadFile = File(...)):
    content = await file.read()
    encoded = base64.b64encode(content).decode("utf-8")
    update_result = await db.sprites.update_one(
        {"_id": ObjectId(sprite_id)},
        {"$set": {
            "filename": file.filename,
            "content_base64": encoded,
            "content_type": file.content_type
        }}
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sprite not found")
    return {"message": "Sprite updated"}

@app.put("/update_audio/{audio_id}")
async def update_audio(audio_id: str, file: UploadFile = File(...)):
    content = await file.read()
    encoded = base64.b64encode(content).decode("utf-8")
    update_result = await db.audio.update_one(
        {"_id": ObjectId(audio_id)},
        {"$set": {
            "filename": file.filename,
            "content_base64": encoded,
            "content_type": file.content_type
        }}
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Audio not found")
    return {"message": "Audio updated"}

@app.put("/update_score/{score_id}")
async def update_score(score_id: str, updated_score: PlayerScore):
    update_result = await db.scores.update_one(
        {"_id": ObjectId(score_id)},
        {"$set": updated_score.dict()}
    )
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Score not found")
    return {"message": "Score updated"}

# ----------------------------- DELETE ROUTES -----------------------------

@app.delete("/delete_sprite/{sprite_id}")
async def delete_sprite(sprite_id: str):
    delete_result = await db.sprites.delete_one({"_id": ObjectId(sprite_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sprite not found")
    return {"message": "Sprite deleted"}

@app.delete("/delete_audio/{audio_id}")
async def delete_audio(audio_id: str):
    delete_result = await db.audio.delete_one({"_id": ObjectId(audio_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Audio not found")
    return {"message": "Audio deleted"}

@app.delete("/delete_score/{score_id}")
async def delete_score(score_id: str):
    delete_result = await db.scores.delete_one({"_id": ObjectId(score_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Score not found")
    return {"message": "Score deleted"}


