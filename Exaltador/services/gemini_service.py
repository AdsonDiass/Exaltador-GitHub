import os
import httpx
from dotenv import load_dotenv

load_dotenv()

# API Keys
API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# URLs
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"


# Função para buscar perfil do GitHub
async def buscar_perfil_github(usuario: str):
    url = f"https://api.github.com/users/{usuario}"
    headers = {
        "Accept": "application/vnd.github+json"
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code == 404:
            raise Exception(f"Usuário '{usuario}' não encontrado no GitHub.")

        response.raise_for_status()
        return response.json()


# Função para buscar repositórios do GitHub
async def buscar_repositorios_github(usuario: str):
    url = f"https://api.github.com/users/{usuario}/repos"
    headers = {
        "Accept": "application/vnd.github+json"
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code == 404:
            raise Exception(f"Repositórios do usuário '{usuario}' não encontrados.")

        response.raise_for_status()
        return response.json()


# Função para chamar o Gemini e gerar texto
async def chamar_gemini(texto: str) -> str:
    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Crie uma mensagem extremamente criativa, empolgante, divertida e carismática "
                            f"para destacar o perfil GitHub a partir das informações a seguir:\n\n{texto}"
                        )
                    }
                ]
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GEMINI_URL, headers=headers, json=body)
        response.raise_for_status()
        resultado = response.json()

        try:
            return resultado["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise Exception("Erro ao processar a resposta do Gemini. Verifique sua chave API ou o conteúdo enviado.")


# Função principal que integra tudo
async def exaltar_perfil(usuario: str):
    perfil = await buscar_perfil_github(usuario)
    repositorios = await buscar_repositorios_github(usuario)

    nome_usuario = perfil.get('name') or usuario
    descricao_usuario = perfil.get('bio', 'Sem descrição disponível.')
    seguidores = perfil.get('followers', 0)
    num_repositorios = len(repositorios)

    resposta_base = (
        f"Prepare-se para conhecer o incrível perfil de {nome_usuario} no GitHub!\n\n"
        f"✨ Descrição: {descricao_usuario}\n"
        f"👥 Seguidores: {seguidores}\n"
        f"📦 Total de repositórios: {num_repositorios}\n\n"
        f"🛠️ Destaques dos repositórios:\n"
    )

    repos_ordenados = sorted(repositorios, key=lambda r: r.get('stargazers_count', 0), reverse=True)

    for repo in repos_ordenados[:5]:  # Top 5 repositórios
        nome = repo.get('name', 'Sem nome')
        descricao = repo.get('description') or 'Sem descrição'
        estrelas = repo.get('stargazers_count', 0)
        resposta_base += f"- ⭐ {nome}: {descricao} (⭐ {estrelas} estrelas)\n"

    resposta_base += "\n🚀 Siga e acompanhe esse dev incrível no GitHub!"

    # Passa para o Gemini gerar a resposta final aprimorada
    return await chamar_gemini(resposta_base)




# ... (código existente) ...

async def chamar_gemini(texto: str) -> str:
    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Crie uma mensagem extremamente criativa, empolgante, divertida e carismática "
                            f"para destacar o perfil GitHub a partir das informações a seguir:\n\n{texto}"
                        )
                    }
                ]
            }
        ]
    }

    # --- ADICIONE ESTAS LINHAS DE DEPURACÃO AQUI ---
    print(f"DEBUG_GEMINI_PROMPT: Prompt completo enviado ao Gemini: {body['contents'][0]['parts'][0]['text'][:500]}...") # Imprime os primeiros 500 caracteres
    # -----------------------------------------------

    async with httpx.AsyncClient() as client:
        response = await client.post(GEMINI_URL, headers=headers, json=body)
        response.raise_for_status()
        resultado = response.json()

        # --- ADICIONE ESTAS LINHAS DE DEPURACÃO AQUI ---
        print(f"DEBUG_GEMINI_RAW_RESPONSE: Resposta bruta do Gemini: {resultado}")
        # -----------------------------------------------

        try:
            final_text = resultado["candidates"][0]["content"]["parts"][0]["text"]
            print(f"DEBUG_GEMINI_EXTRACTED_TEXT: Texto extraído do Gemini: {final_text}")
            return final_text
        except (KeyError, IndexError) as e:
            print(f"DEBUG_GEMINI_ERROR_EXTRACT: Erro ao extrair texto do Gemini. Resposta: {resultado}. Erro: {e}")
            raise Exception("Erro ao processar a resposta do Gemini. Verifique sua chave API ou o conteúdo enviado.")


# ... (restante do código) ...
