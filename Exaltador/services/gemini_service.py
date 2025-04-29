import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + API_KEY

# Função para buscar perfil do GitHub
async def buscar_perfil_github(usuario: str):
    url = f"https://api.github.com/users/{usuario}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

# Função para buscar repositórios do GitHub
async def buscar_repositorios_github(usuario: str):
    url = f"https://api.github.com/users/{usuario}/repos"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

# Função para gerar conteúdo criativo com o Gemini
async def chamar_gemini(texto: str) -> str:
    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "contents": [
            {
                "parts": [
                    {"text": f"Exalte o perfil de GitHub com entusiasmo e criatividade: {texto}"}
                ]
            }
        ]
    }

    params = {"key": API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.post(GEMINI_URL, headers=headers, json=body, params=params)
        response.raise_for_status()
        resultado = response.json()
        return resultado["candidates"][0]["content"]["parts"][0]["text"]

# Função para combinar as informações do perfil e repositórios e gerar a resposta
async def exaltar_perfil(usuario: str):
    perfil = await buscar_perfil_github(usuario)
    repositorios = await buscar_repositorios_github(usuario)

    nome_usuario = perfil.get('name', 'Desconhecido')
    descricao_usuario = perfil.get('bio', 'Sem descrição')
    num_repositorios = len(repositorios)
    seguidores = perfil.get('followers', 0)

    resposta_base = f"Preparem-se para conhecer o perfil de GitHub de {nome_usuario}!\n\n"
    resposta_base += f"Este usuário tem uma descrição impressionante: {descricao_usuario}\n"
    resposta_base += f"Com {seguidores} seguidores, {nome_usuario} é uma figura notável no mundo do desenvolvimento.\n\n"
    resposta_base += f"Mas o verdadeiro brilho de {nome_usuario} está nos seus {num_repositorios} repositórios, onde soluções incríveis e criativas são constantemente publicadas!\n\n"
    resposta_base += f"**Repositórios mais populares:**\n"
    
    for repo in repositorios[:5]:  # Apenas os 5 primeiros repositórios
        resposta_base += f"- {repo['name']}: {repo['description'] if repo['description'] else 'Sem descrição'}\n"

    resposta_base += f"\n**Siga {nome_usuario} e prepare-se para uma jornada incrível no mundo do código!** 🚀💻"

    # Passar a resposta base para o Gemini aprimorar
    return await chamar_gemini(resposta_base)
