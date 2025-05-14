from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models.prompt import Prompt
from services.gemini_service import exaltar_perfil

app = FastAPI()

# Montar arquivos estáticos (CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar pasta de templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/exaltar")
async def exaltar(prompt: Prompt):
    resposta = await exaltar_perfil(prompt.texto)
    return {"resposta": resposta}
