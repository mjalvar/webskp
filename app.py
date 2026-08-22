import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Evitar fallos de globalización en Linux/Fly.io
os.environ["DOTNET_SYSTEM_GLOBALIZATION_INVARIANT"] = "1"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "static/models"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from datetime import datetime

APP_VERSION = os.getenv("APP_VERSION") or os.getenv("VRTOUR_VERSION") or os.getenv("GIT_SHA") or f"dev-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    print(f"[BOOT] app_version={APP_VERSION}")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Carga la interfaz del Tour Virtual"""
    return templates.TemplateResponse("index.html", {"request": request, "app_version": APP_VERSION})


@app.get("/models")
async def list_models():
    """Escanea la carpeta del servidor y devuelve una lista de archivos .glb"""
    try:
        archivos = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith('.glb')]
        return {"success": True, "models": archivos}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Recibe y guarda el archivo .glb con su nombre original"""
    if not file.filename.lower().endswith('.glb'):
        return {"success": False, "error": "Por favor, sube un archivo binario .glb"}
    
    # Limpiamos el nombre de espacios para evitar fallos de URL en el navegador
    safe_filename = file.filename.replace(" ", "_")
    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
            
        return {
            "success": True, 
            "model_url": f"/static/models/{safe_filename}",
            "filename": safe_filename
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"success": False, "error": f"Error al guardar: {str(e)}"}


@app.post("/hudlog")
async def hud_log(request: Request):
    """Receive HUD debug lines from the client and log them server-side for remote debugging (appears in fly logs)."""
    try:
        data = await request.json()
        text = data.get('text') if isinstance(data, dict) else str(data)
        # Simple print so it appears in container logs (fly logs)
        print(f"[VR-HUD-REMOTE] {text}")
        return JSONResponse({"success": True})
    except Exception as e:
        print(f"[VR-HUD-REMOTE] failed to log hud: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
