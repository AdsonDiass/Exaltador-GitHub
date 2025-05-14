from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from models.prompt import Prompt
from services.gemini_service import exaltar_perfil

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Exaltador de Perfis GitHub</title>
        </head>
        <body>
            <h1>🚀 Bem-vindo ao Exaltador de Perfis GitHub!</h1>
            <p>Use a rota <a href="/docs">/docs</a> para testar a API interativa.</p>
        </body>
    </html>
    """

@app.post("/exaltar")
async def exaltar(prompt: Prompt):
    resposta = await exaltar_perfil(prompt.texto)
    return {"resposta": resposta}
