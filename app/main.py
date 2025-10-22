from fastapi import FastAPI
from app.routers import pets, users

app = FastAPI(title="Pet Finder API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(pets.router)
app.include_router(users.router)