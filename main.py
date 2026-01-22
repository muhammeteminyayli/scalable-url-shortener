from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import uvicorn
from database import create_db_and_tables
from services import worker


# --- Pydantic Models ---
class URLItem(BaseModel):
    url: str


# --- Lifespan Manager ---
# Manages the startup and shutdown events of the application.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database
    print("🔄 Checking database tables...")
    create_db_and_tables()
    print("✅ System started successfully!")

    yield  # Application runs here

    # Shutdown: Clean up resources if needed
    print("System shutting down... Goodbye!")


# --- Application Initialization ---
app = FastAPI(lifespan=lifespan, title="URL Shortener Service")


# --- Endpoints ---

@app.get("/")
def home():
    """ Test endpoint to verify the service is running. """
    return {"message": "Welcome to the URL Shortener Service!"}


@app.post("/shorten")
def shorten_url_endpoint(item: URLItem):
    """
    Accepts a long URL, creates a short code for it, and returns the shortened link.
    """
    short_code = worker.shorten_url(item.url)
    # Ideally, the base URL should be dynamic based on the request or configuration
    full_link = f"http://127.0.0.1:8000/{short_code}"
    return {"original": item.url, "short_link": full_link}


@app.get("/{short_code}")
def redirect_to_original(short_code: str):
    """
    Takes a short code, looks up the original URL, and redirects the user.
    """
    original_url = worker.get_original_url(short_code)
    if original_url:
        return RedirectResponse(url=original_url)
    else:
        raise HTTPException(status_code=404, detail="Link not found")


if __name__ == "__main__":
    print("🚀 Server Starting... Go to http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)