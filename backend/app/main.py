from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, data, dashboard

app = FastAPI(title="BSM Reproduction Guide API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    return {"message": "BSM Reproduction Guide API is running"}
