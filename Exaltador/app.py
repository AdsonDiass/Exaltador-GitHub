from fastapi import FastAPI
from models.prompt import Prompt
from services.gemini_service import exaltar_perfil

app = FastAPI()

@app.post("/exaltar")
async def exaltar(prompt: Prompt):
    # Exaltar o perfil do GitHub
    resposta = await exaltar_perfil(prompt.texto)
    return {"resposta": resposta}
