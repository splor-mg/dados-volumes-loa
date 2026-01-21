import os
import yaml
import requests
from urllib.parse import quote
from dotenv import load_dotenv

# Define o diretório raiz do projeto (um nível acima de scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Carrega variáveis de ambiente do arquivo .env na raiz do projeto
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# =========================
# CONFIGURAÇÃO
# =========================

# Credenciais do Azure AD
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Validação de variáveis obrigatórias
if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
    raise ValueError(
        "Variáveis de ambiente obrigatórias não configuradas. "
        "Verifique se o arquivo .env existe e contém: TENANT_ID, CLIENT_ID, CLIENT_SECRET"
    )

TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/token"
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

# =========================
# AUTH
# =========================

def get_access_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "resource": "https://graph.microsoft.com"
    }

    r = requests.post(TOKEN_URL, data=data)
    if not r.ok:
        raise RuntimeError(f"Erro ao obter token: {r.status_code} - {r.text}")

    return r.json()["access_token"]

# =========================
# GRAPH HELPERS
# =========================

def graph_get(url, token):
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if not r.ok:
        raise RuntimeError(f"Erro Graph {r.status_code}: {r.text}")
    return r.json()

def url_to_site_path(sharepoint_url):
    """
    Converte URL do SharePoint para formato do Graph API.
    Ex: https://cecad365.sharepoint.com/sites/SPLOR/ -> cecad365.sharepoint.com:/sites/SPLOR
    """
    # Remove https:// e trailing slash
    url = sharepoint_url.rstrip('/').replace('https://', '')
    # Substitui o primeiro / por :/
    if '/' in url:
        parts = url.split('/', 1)
        return f"{parts[0]}:/{parts[1]}"
    return url

def get_site_id(token, site_path):
    """Obtém o ID do site usando o caminho do site."""
    url = f"{GRAPH_BASE}/sites/{site_path}"
    return graph_get(url, token)["id"]

def get_drive_id_by_name(token, site_id, drive_name):
    """Obtém o ID do drive pelo nome."""
    url = f"{GRAPH_BASE}/sites/{site_id}/drives"
    drives = graph_get(url, token)["value"]
    
    for drive in drives:
        if drive["name"] == drive_name:
            return drive["id"]
    
    raise RuntimeError(f"Drive '{drive_name}' não encontrado no site")

def get_item_by_path(token, drive_id, item_path):
    """Obtém informações de um item pelo caminho relativo à root do drive."""
    # Remove leading slash se existir
    item_path = item_path.lstrip('/')
    encoded_path = quote(item_path)
    url = f"{GRAPH_BASE}/drives/{drive_id}/root:/{encoded_path}"
    return graph_get(url, token)

# =========================
# DOWNLOAD
# =========================

def download_file(url, local_path, token):
    """Baixa um arquivo do SharePoint."""
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    with requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        stream=True
    ) as r:
        if not r.ok:
            raise RuntimeError(f"Erro download {r.status_code}: {r.text}")

        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def download_item(token, drive_id, item_path, local_path):
    """Baixa um item específico do SharePoint."""
    # Obtém informações do item
    item = get_item_by_path(token, drive_id, item_path)
    
    if "file" not in item:
        raise RuntimeError(f"O item '{item_path}' não é um arquivo")
    
    # URL para download do conteúdo
    download_url = f"{GRAPH_BASE}/drives/{drive_id}/items/{item['id']}/content"
    
    print(f"Baixando: {item_path} -> {local_path}")
    download_file(download_url, local_path, token)
    print(f"✓ Concluído: {local_path}")

# =========================
# MAIN
# =========================

def main():
    # Lê o arquivo datapackage.yaml na raiz do projeto
    datapackage_filename = os.getenv("DATAPACKAGE_PATH", "datapackage.yaml")
    datapackage_path = os.path.join(PROJECT_ROOT, datapackage_filename)
    
    if not os.path.exists(datapackage_path):
        raise FileNotFoundError(f"Arquivo {datapackage_path} não encontrado")
    
    with open(datapackage_path, 'r', encoding='utf-8') as f:
        datapackage = yaml.safe_load(f)
    
    if 'resources' not in datapackage:
        raise ValueError("Arquivo datapackage.yaml não contém 'resources'")
    
    # Obtém token de autenticação
    print("Obtendo token de autenticação...")
    token = get_access_token()
    print("✓ Autenticação realizada com sucesso\n")
    
    # Processa cada resource
    resources = datapackage['resources']
    print(f"Total de recursos a processar: {len(resources)}\n")
    
    for idx, resource in enumerate(resources, 1):
        try:
            # Valida estrutura do resource
            if 'sharepoint' not in resource:
                print(f"[{idx}/{len(resources)}] ⚠ Pulando resource '{resource.get('name', 'sem nome')}': sem configuração sharepoint")
                continue
            
            sp_config = resource['sharepoint']
            if 'path' not in sp_config or 'drive' not in sp_config or 'item' not in sp_config:
                print(f"[{idx}/{len(resources)}] ⚠ Pulando resource '{resource.get('name', 'sem nome')}': configuração sharepoint incompleta")
                continue
            
            if 'path' not in resource:
                print(f"[{idx}/{len(resources)}] ⚠ Pulando resource '{resource.get('name', 'sem nome')}': sem caminho local especificado")
                continue
            
            # Extrai informações
            sharepoint_path = sp_config['path']
            drive_name = sp_config['drive']
            item_path = sp_config['item']
            local_path = resource['path']
            
            print(f"[{idx}/{len(resources)}] Processando: {resource.get('name', 'sem nome')}")
            
            # Converte URL do SharePoint para formato do Graph API
            site_path = url_to_site_path(sharepoint_path)
            
            # Obtém IDs necessários
            site_id = get_site_id(token, site_path)
            drive_id = get_drive_id_by_name(token, site_id, drive_name)
            
            # Baixa o item
            download_item(token, drive_id, item_path, local_path)
            print()
            
        except Exception as e:
            print(f"[{idx}/{len(resources)}] ✗ Erro ao processar resource '{resource.get('name', 'sem nome')}': {str(e)}\n")
            continue
    
    print("Processamento concluído!")

if __name__ == "__main__":
    main()
