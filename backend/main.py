import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StoryRequest(BaseModel):
    genre: str
    runtime: int
    character_count: int

class StoryResponse(BaseModel):
    storyline: str

@app.post("/generate", response_model=StoryResponse)
async def generate_story(req: StoryRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not set.")
    prompt = (
        f"Write a creative {req.genre} movie storyline that is suitable for a runtime of "
        f"{req.runtime} minutes and involves approximately {req.character_count} main characters. "
        "Make it imaginative, engaging, and suitable for a short film or feature-length production."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.85,
        )
        storyline = response.choices[0].message["content"].strip()
        return StoryResponse(storyline=storyline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 