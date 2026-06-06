import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import chat

app = FastAPI()

#env
USE_S3 = os.getenv("USE_S3", False)

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add routers
app.include_router(chat.router)


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.get("/health")
async def health():
    return {"message": "healthy","use_s3" : USE_S3}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
