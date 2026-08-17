import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Configuración obligatoria para evitar fallos de globalización en Linux
os.environ["DOTNET_SYSTEM_GLOBALIZATION_INVARIANT"] = "1"

app = FastAPI()

# Middleware CORS: Permite que el frontend se comunique con el backend 
# sin bloqueos de seguridad del navegador (Crucial para desarrollo local y Ngrok)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar y asegurar la existencia de las carpetas de almacenamiento
UPLOAD_FOLDER = "static/models"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Montar los archivos estáticos y las plantillas HTML
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Sirve la interfaz web del Tour Virtual con el visor A-Frame"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Recibe el archivo .glb optimizado y lo almacena para las Meta Quest 3"""
    # Validación estricta del formato web 3D binario
    if not file.filename.lower().endswith('.glb'):
        return {"success": False, "error": "Por favor, sube un archivo en formato binario .glb"}
    
    # Construir la ruta de guardado definitiva
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    try:
        # Guardar el archivo recibido en el almacenamiento del servidor
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
            
        return {
            "success": True, 
            "model_url": f"/static/models/{file.filename}"
        }
    except Exception as e:
        # Limpieza en caso de una subida corrupta o incompleta
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"success": False, "error": f"Error al guardar el archivo: {str(e)}"}
