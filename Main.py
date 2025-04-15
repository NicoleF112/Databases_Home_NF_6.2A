from fastapi import FastAPI, File, UploadFile, HTTPException # This is used to create the API and handle file uploads
from pydantic import BaseModel # This is used to create the data model for the player score
import motor.motor_asyncio # This is used to connect to MongoDB Atlas
import base64 # This is used to encode the file content to base64
from bson import ObjectId # This is used to convert the ID from the database to a string
from dotenv import load_dotenv
import os

app = FastAPI() # This creates the FastAPI app

# Load environment variables from .env file
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL") # This loads the MongoDB connection string from the environment variables
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL) # This is the connection string to MongoDB Atlas
db = client["DatabaseEssensials62A"]  # Make sure the DB name matches Atlas exactly

# To Prevent SQL injection attacks, we use Pydantic to validate the data
# Since player_name and score are required fields, we define them in the PlayerScore model 
# and this helps us prevent SQL injection attacks by validating the data before inserting it into the database
class PlayerScore(BaseModel): 
    player_name: str
    score: int

# ----------------------------- UPLOAD ROUTES -----------------------------

# This route is used to upload one or more sprite files
# Accepts multiple image files via form-data, encodes them in base64, and stores them in MongoDB
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)): # This is used to upload the sprite file
    content = await file.read()
    encoded = base64.b64encode(content).decode("utf-8") # This encodes the file content to base64
    sprite_doc = { # This is the document that will be stored in the database
        "filename": file.filename,
        "content_base64": encoded,
        "content_type": file.content_type
    }
    result = await db.sprites.insert_one(sprite_doc) # This inserts the document into the database
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}# This returns the ID of the inserted document

# This route is used to upload one or more audio files
# Accepts multiple audio files via form-data, encodes them in base64, and stores them in MongoDB
@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)): # This is used to upload the audio file
    content = await file.read()
    encoded = base64.b64encode(content).decode("utf-8") # This encodes the file content to base64
    audio_doc = { # This is the document that will be stored in the database
        "filename": file.filename,
        "content_base64": encoded,
        "content_type": file.content_type
    }
    result = await db.audio.insert_one(audio_doc) # This inserts the document into the database
    return {"message": "Audio uploaded", "id": str(result.inserted_id)} # This returns the ID of the inserted document

# This route is used to upload a player score
# Accepts a JSON object with player name and score, and stores it in MongoDB
@app.post("/player_score")
async def add_score(score: PlayerScore): # This is used to upload the player score
    result = await db.scores.insert_one(score.dict()) # This inserts the document into the database
    return {"message": "Score recorded", "id": str(result.inserted_id)} # This returns the ID of the inserted document

# ----------------------------- RETRIEVAL ROUTES -----------------------------

# This route is used to retrieve a sprite by its ID
# It accepts the sprite ID as a path parameter and returns the sprite document from MongoDB
@app.get("/get_sprite/{sprite_id}")
async def get_sprite(sprite_id: str): # This is used to retrieve the sprite by its ID
    sprite = await db.sprites.find_one({"_id": ObjectId(sprite_id)}) # This retrieves the sprite document from the database
    if not sprite:
        raise HTTPException(status_code=404, detail="Sprite not found") # This raises an error if the sprite is not found
    return sprite # This returns the sprite document

# This route is used to retrieve an audio file by its ID
# It accepts the audio ID as a path parameter and returns the audio document from MongoDB
@app.get("/get_audio/{audio_id}")
async def get_audio(audio_id: str): # This is used to retrieve the audio by its ID
    audio = await db.audio.find_one({"_id": ObjectId(audio_id)}) # This retrieves the audio document from the database
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found") # This raises an error if the audio is not found
    return audio # This returns the audio document

# This route is used to retrieve a player score by its ID
# It accepts the score ID as a path parameter and returns the score document from MongoDB
@app.get("/get_score/{score_id}")
async def get_score(score_id: str): # This is used to retrieve the score by its ID
    score = await db.scores.find_one({"_id": ObjectId(score_id)}) # This retrieves the score document from the database
    if not score:
        raise HTTPException(status_code=404, detail="Score not found") # This raises an error if the score is not found
    return score # This returns the score document

# ----------------------------- UPDATE ROUTES -----------------------------

# This route is used to update a sprite by its ID
# It accepts the sprite ID as a path parameter and the new file as form-data
@app.put("/update_sprite/{sprite_id}")
async def update_sprite(sprite_id: str, file: UploadFile = File(...)): # This is used to update the sprite file
    content = await file.read() # This reads the content of the file
    encoded = base64.b64encode(content).decode("utf-8") # This encodes the file content to base64
    update_result = await db.sprites.update_one(  # This updates the sprite document in the database
        {"_id": ObjectId(sprite_id)},
        {"$set": {
            "filename": file.filename,
            "content_base64": encoded,
            "content_type": file.content_type
        }}
    )
    if update_result.matched_count == 0: # This checks if the sprite was found in the database
        raise HTTPException(status_code=404, detail="Sprite not found") # This raises an error if the sprite is not found
    return {"message": "Sprite updated"} # This returns a message indicating that the sprite was updated

# This route is used to update an audio file by its ID
# It accepts the audio ID as a path parameter and the new file as form-data
@app.put("/update_audio/{audio_id}") 
async def update_audio(audio_id: str, file: UploadFile = File(...)): # This is used to update the audio file
    content = await file.read() # This reads the content of the file
    encoded = base64.b64encode(content).decode("utf-8") # This encodes the file content to base64
    update_result = await db.audio.update_one(   # This updates the audio document in the database
        {"_id": ObjectId(audio_id)}, 
        {"$set": {
            "filename": file.filename,
            "content_base64": encoded,
            "content_type": file.content_type
        }}
    )
    if update_result.matched_count == 0: # This checks if the audio was found in the database
        raise HTTPException(status_code=404, detail="Audio not found") # This raises an error if the audio is not found
    return {"message": "Audio updated"} # This returns a message indicating that the audio was updated

# This route is used to update a player score by its ID
# It accepts the score ID as a path parameter and the new score as JSON
@app.put("/update_score/{score_id}") 
async def update_score(score_id: str, updated_score: PlayerScore): # This is used to update the player score
    update_result = await db.scores.update_one( # This updates the score document in the database
        {"_id": ObjectId(score_id)},
        {"$set": updated_score.dict()}
    )
    if update_result.matched_count == 0: # This checks if the score was found in the database
        raise HTTPException(status_code=404, detail="Score not found") # This raises an error if the score is not found
    return {"message": "Score updated"} # This returns a message indicating that the score was updated

# ----------------------------- DELETE ROUTES -----------------------------

# This route is used to delete a sprite by its ID
# It accepts the sprite ID as a path parameter and deletes the sprite document from MongoDB
@app.delete("/delete_sprite/{sprite_id}")
async def delete_sprite(sprite_id: str): # This is used to delete the sprite by its ID
    delete_result = await db.sprites.delete_one({"_id": ObjectId(sprite_id)}) # This deletes the sprite document from the database
    if delete_result.deleted_count == 0: # This checks if the sprite was found in the database
        raise HTTPException(status_code=404, detail="Sprite not found") # This raises an error if the sprite is not found
    return {"message": "Sprite deleted"} # This returns a message indicating that the sprite was deleted

# This route is used to delete an audio file by its ID
# It accepts the audio ID as a path parameter and deletes the audio document from MongoDB
@app.delete("/delete_audio/{audio_id}") # This is used to delete the audio by its ID
async def delete_audio(audio_id: str): # This is used to delete the audio file
    delete_result = await db.audio.delete_one({"_id": ObjectId(audio_id)}) # This deletes the audio document from the database
    if delete_result.deleted_count == 0: # This checks if the audio was found in the database
        raise HTTPException(status_code=404, detail="Audio not found") # This raises an error if the audio is not found
    return {"message": "Audio deleted"} # This returns a message indicating that the audio was deleted


# This route is used to delete a player score by its ID
# It accepts the score ID as a path parameter and deletes the score document from MongoDB
@app.delete("/delete_score/{score_id}") # This is used to delete the score by its ID
async def delete_score(score_id: str): # This is used to delete the player score
    delete_result = await db.scores.delete_one({"_id": ObjectId(score_id)}) # This deletes the score document from the database
    if delete_result.deleted_count == 0: # This checks if the score was found in the database
        raise HTTPException(status_code=404, detail="Score not found") # This raises an error if the score is not found
    return {"message": "Score deleted"} # This returns a message indicating that the score was deleted