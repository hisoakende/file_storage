from fastapi import FastAPI
from interfaces.api import router as api_router
from dependencies import MONGODB_URL, MONGODB_DB_NAME, STORAGE_PATH, SECRET_KEY
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="File Storage API")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to File Storage API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
