import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx # Importado para fazer requisições HTTP

from models.prompt import Prompt
from services.gemini_service import exaltar_perfil

app = FastAPI()

# Montar arquivos estáticos (CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar pasta de templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Rota principal que renderiza a página inicial.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/exaltar")
async def exaltar(prompt: Prompt):
    """
    Rota para exaltar um perfil do GitHub usando o serviço Gemini.
    Recebe um Prompt contendo o texto (username do GitHub).
    """
    try:
        resposta = await exaltar_perfil(prompt.texto)
        return {"resposta": resposta}
    except Exception as e:
        # Adiciona um log em caso de erro na função exaltar_perfil
        print(f"DEBUG_EXALTAR_ERROR: Erro ao chamar exaltar_perfil: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro ao exaltar o perfil: {str(e)}"}
        )


@app.get("/github/{username}")
async def get_github_user(username: str):
    """
    Rota para buscar informações de um usuário do GitHub diretamente.
    Esta rota é chamada internamente pelo seu frontend ou pode ser testada diretamente.
    """
    url = f"https://api.github.com/users/{username}"

    # Recupera o token do ambiente
    github_token = os.getenv("GITHUB_TOKEN")

    # --- INÍCIO DAS LINHAS DE DEPURACÃO CRUCIAIS ---
    # Verifica se o token foi carregado do ambiente
    if github_token:
        # Imprime apenas o início e o fim do token por segurança, NUNCA O TOKEN COMPLETO!
        print(f"DEBUG_TOKEN: GITHUB_TOKEN loaded (partial): {github_token[:5]}...{github_token[-5:]}")
    else:
        print("DEBUG_TOKEN: GITHUB_TOKEN is NOT loaded (it's None or empty).")
    # --- FIM DAS LINHAS DE DEPURACÃO DO TOKEN ---

    headers = {
        "Accept": "application/vnd.github+json"
    }

    # Se o token existir, adiciona-o ao cabeçalho de Autorização
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    # --- INÍCIO DA LINHA DE DEPURACÃO DOS HEADERS ENVIADOS ---
    # Mostra quais cabeçalhos estão sendo enviados na requisição HTTP
    print(f"DEBUG_HEADERS: Headers sent to GitHub API: {headers}")
    # --- FIM DA LINHA DE DEPURACÃO DOS HEADERS ---

    try:
        async with httpx.AsyncClient() as client:
            # Faz a requisição GET para a API do GitHub
            response = await client.get(url, headers=headers, timeout=10)
            # Levanta uma exceção se a resposta não for 2xx (sucesso)
            response.raise_for_status()
            # Retorna a resposta JSON da API do GitHub
            return response.json()

    except httpx.HTTPStatusError as e:
        # --- INÍCIO DA LINHA DE DEPURACÃO DO ERRO BRUTO DO GITHUB ---
        # Captura erros HTTP (como 401, 404, 403) e imprime detalhes
        print(f"DEBUG_ERROR_GITHUB: GitHub API returned {e.response.status_code} for URL {e.request.url} with content: {e.response.text}")
        # --- FIM DA LINHA DE DEPURACÃO DO ERRO BRUTO DO GITHUB ---
        # Retorna uma resposta JSON com o status do erro e a mensagem da API
        return JSONResponse(
            status_code=e.response.status_code,
            content={"error": f"Erro HTTP {e.response.status_code}: {e.response.reason_phrase}"}
        )

    except Exception as e:
        # Captura qualquer outra exceção inesperada
        print(f"DEBUG_GENERIC_ERROR: Erro inesperado em get_github_user: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro inesperado: {str(e)}"}
        )
