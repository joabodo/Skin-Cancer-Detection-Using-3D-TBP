from fastapi import FastAPI, Request, HTTPException
from .core import database, config, logging_conf
from .routers import auth, inference, patients, admin, users
from fastapi.middleware.cors import CORSMiddleware
import aioredis, asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta

settings = config.settings
app = FastAPI(title="Skin Cancer Detection API - PROD")

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple rate limiting middleware using Redis
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url:str, limit_per_min:int):
        super().__init__(app)
        self.redis_url = redis_url
        self.limit = limit_per_min
        self._redis = None

    async def dispatch(self, request: Request, call_next):
        if self._redis is None:
            self._redis = await aioredis.from_url(self.redis_url)
        identifier = request.client.host or "anonymous"
        key = f"rl:{identifier}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        cur = await self._redis.incr(key)
        if cur == 1:
            await self._redis.expire(key, 60)
        if cur > self.limit:
            raise HTTPException(status_code=429, detail="Too many requests")
        response = await call_next(request)
        return response

app.add_middleware(RateLimitMiddleware, redis_url=settings.REDIS_URL, limit_per_min=settings.RATE_LIMIT_PER_MIN)

# create tables
database.Base.metadata.create_all(bind=database.engine)

# include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(patients.router)
app.include_router(inference.router)
app.include_router(admin.router)


@app.get('/healthz')
def health():
    return {"status":"ok"}
