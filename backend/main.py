#backend/main.py
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import asyncio

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OpenAI API key not set.")

client = OpenAI(api_key=OPENAI_API_KEY)
executor = ThreadPoolExecutor(max_workers=4)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plotpop")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StoryRequest(BaseModel):
    genre: str = Field(..., min_length=3, max_length=32)
    runtime: int = Field(..., ge=10, le=240)
    character_count: int = Field(..., ge=1, le=10)

class StoryResponse(BaseModel):
    storyline: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

async def generate_openai_story(prompt: str):
    loop = asyncio.get_event_loop()
    def call_openai():
        return client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.85,
        )
    return await loop.run_in_executor(executor, call_openai)

@app.post("/generate", response_model=StoryResponse)
async def generate_story(req: StoryRequest):
    prompt = (
        f"Write a creative {req.genre} movie storyline that is suitable for a runtime of "
        f"{req.runtime} minutes and involves approximately {req.character_count} main characters. "
        "Make it imaginative, engaging, and suitable for a short film or feature-length production."
    )
    logger.info(f"Generating story: genre={req.genre}, runtime={req.runtime}, characters={req.character_count}")
    try:
        response = await generate_openai_story(prompt)
        storyline = response.choices[0].message.content.strip()
        return StoryResponse(storyline=storyline)
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate storyline.") 
