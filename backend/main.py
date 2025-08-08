import os
import logging
import time
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import asyncio
from datetime import datetime, timedelta
import hashlib
import json

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OpenAI API key not set.")

client = OpenAI(api_key=OPENAI_API_KEY)
executor = ThreadPoolExecutor(max_workers=4)


cache = {}
CACHE_TTL = 3600  

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("plotpop")

app = FastAPI(
    title="PlotPOP API",
    description="AI-powered movie storyline generator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {process_time:.3f}s")
    return response

class StoryRequest(BaseModel):
    genre: str = Field(..., min_length=3, max_length=32, description="Movie genre (e.g., 'Sci-Fi', 'Romance')")
    runtime: int = Field(..., ge=10, le=240, description="Movie runtime in minutes")
    character_count: int = Field(..., ge=1, le=10, description="Number of main characters")
    
    @validator('genre')
    def validate_genre(cls, v):
        valid_genres = [
            'Action', 'Adventure', 'Comedy', 'Drama', 'Horror', 'Mystery', 
            'Romance', 'Sci-Fi', 'Thriller', 'Western', 'Fantasy', 'Animation',
            'Documentary', 'Musical', 'War', 'Crime', 'Biography', 'History'
        ]
        if v.title() not in valid_genres:
            raise ValueError(f"Genre must be one of: {', '.join(valid_genres)}")
        return v.title()

class StoryResponse(BaseModel):
    storyline: str
    generated_at: datetime
    cache_hit: bool = False

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    uptime: float
    cache_size: int

# Global variables for health check
start_time = time.time()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(),
        uptime=time.time() - start_time,
        cache_size=len(cache)
    )

def get_cache_key(genre: str, runtime: int, character_count: int) -> str:
    """Generate cache key for request parameters"""
    key_data = f"{genre}:{runtime}:{character_count}"
    return hashlib.md5(key_data.encode()).hexdigest()

def cleanup_expired_cache():
    """Remove expired cache entries"""
    current_time = datetime.now()
    expired_keys = [
        key for key, (_, timestamp) in cache.items()
        if current_time - timestamp > timedelta(seconds=CACHE_TTL)
    ]
    for key in expired_keys:
        del cache[key]
    if expired_keys:
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

async def generate_openai_story(prompt: str):
    """Generate story using OpenAI API in thread pool"""
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
    """
    Generate a creative movie storyline based on provided parameters.
    
    - **genre**: Movie genre (e.g., 'Sci-Fi', 'Romance')
    - **runtime**: Movie runtime in minutes (10-240)
    - **character_count**: Number of main characters (1-10)
    """
    # Cleanup expired cache entries
    cleanup_expired_cache()
    
    # Check cache first
    cache_key = get_cache_key(req.genre, req.runtime, req.character_count)
    if cache_key in cache:
        storyline, _ = cache[cache_key]
        logger.info(f"Cache hit for request: {cache_key}")
        return StoryResponse(
            storyline=storyline,
            generated_at=datetime.now(),
            cache_hit=True
        )
    
    prompt = (
        f"Write a creative {req.genre} movie storyline that is suitable for a runtime of "
        f"{req.runtime} minutes and involves approximately {req.character_count} main characters. "
        "Make it imaginative, engaging, and suitable for a short film or feature-length production. "
        "Include a brief synopsis, main plot points, and character descriptions."
    )
    
    logger.info(f"Generating story: genre={req.genre}, runtime={req.runtime}, characters={req.character_count}")
    
    try:
        response = await generate_openai_story(prompt)
        storyline = response.choices[0].message.content.strip()
        
        
        cache[cache_key] = (storyline, datetime.now())
        logger.info(f"Cached story with key: {cache_key}")
        
        return StoryResponse(
            storyline=storyline,
            generated_at=datetime.now(),
            cache_hit=False
        )
        
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate storyline. Please try again later."
        )

@app.delete("/cache")
async def clear_cache():
    """Clear all cached storylines"""
    global cache
    cache_size = len(cache)
    cache.clear()
    logger.info(f"Cache cleared. Removed {cache_size} entries")
    return {"message": f"Cache cleared. Removed {cache_size} entries"}

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    cleanup_expired_cache()
    return {
        "total_entries": len(cache),
        "cache_ttl_seconds": CACHE_TTL,
        "memory_usage_mb": len(json.dumps(cache)) / (1024 * 1024)
    } 
