import socket
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, HOST, PORT, BASE_DIR, AUTO_SEED, DATABASE_URL
from app.database import engine, Base
from app.routers import machines_api, inventory_api, maintenance_api, dashboard_api
import seed_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Create tables in PostgreSQL / SQLite
    Base.metadata.create_all(bind=engine)
    
    # 2. Auto-seed if enabled and DB is empty
    if AUTO_SEED:
        try:
            seed_data.seed()
        except Exception as e:
            print(f"[!] Otomatik tohumlama hatasi (onemsiz): {e}")

    yield
    # Shutdown logic (if any)

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan
)

# CORS middleware for local and cloud network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(dashboard_api.router)
app.include_router(machines_api.router)
app.include_router(inventory_api.router)
app.include_router(maintenance_api.router)

# Mount Static Files
static_dir = BASE_DIR / "app" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates_dir = BASE_DIR / "app" / "templates"

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    index_file = templates_dir / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h2>Uygulama yukleniyor...</h2>", status_code=200)

@app.get("/api/system-info")
def get_system_info():
    """Returns the environment and connection details."""
    hostname = socket.gethostname()
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        try:
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            pass

    is_cloud = "railway" in os.getenv("RAILWAY_ENVIRONMENT", "").lower() or bool(os.getenv("RAILWAY_STATIC_URL"))
    db_type = "PostgreSQL" if "postgresql" in DATABASE_URL else "SQLite"

    return {
        "hostname": hostname,
        "local_ip": local_ip,
        "port": PORT,
        "local_url": f"http://localhost:{PORT}",
        "lan_url": f"http://{local_ip}:{PORT}",
        "database_type": db_type,
        "is_cloud": is_cloud
    }

if __name__ == "__main__":
    import uvicorn
    info = get_system_info()
    print("=" * 60)
    print(f"[*] {APP_TITLE} Baslatiliyor...")
    print(f"[*] Veritabani Turu            : {info['database_type']}")
    print(f"[*] Port                       : {PORT}")
    print(f"[*] Yerel Erisim (Local)       : {info['local_url']}")
    print(f"[*] Yerel Ag (LAN) Erisimi     : {info['lan_url']}")
    print(f"[*] API Dokumantasyonu (Docs)  : {info['local_url']}/docs")
    print("=" * 60)
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
