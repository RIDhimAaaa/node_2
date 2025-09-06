from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth.auth import auth_router
from routers.auth.sync import router as sync_router
from routers.users import users_router
from routers.admin.admin import router as admin_router
from routers.trackers.trackers import router as trackers_router


app = FastAPI(
    title="Supabase FastAPI Boilerplate",
    description="A FastAPI application with Supabase authentication and GNDU result tracking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://localhost:5173"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Sarkari Scraper API is running!"}

app.include_router(auth_router)
app.include_router(sync_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(trackers_router)

