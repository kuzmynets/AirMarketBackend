from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.api import ads
from app.api import user
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ads.router)
app.include_router(user.router)

# if __name__ == "__main__":
#      uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)