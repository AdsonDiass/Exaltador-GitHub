from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from fastapi.responses import JSONResponse


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




@app.get("/github/{username}")
async def get_github_user(username: str):
    url = f"https://api.github.com/users/{username}"
    headers = {
        # Se quiser evitar limite de taxa, ative o token abaixo:
        # "Authorization": "token SEU_TOKEN_AQUI"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
    
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            status_code=e.response.status_code,
            content={"error": f"Erro HTTP {e.response.status_code}: {e.response.reason_phrase}"}
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro inesperado: {str(e)}"}
        )

