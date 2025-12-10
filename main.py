import requests
import datetime
import os
from PIL import Image
from io import BytesIO 

API_KEY = os.environ.get('UNSPLASH_ACCESS_KEY') 

UNSPLASH_API_URL = "https://api.unsplash.com/photos/random"
DOWNLOAD_DIR = "wallpapers" 


def get_image_url():
    """
    Liga-se à API do Unsplash para obter uma foto aleatória de alta definição.
    Devolve (image_url, title) ou (None, None) em caso de falha.
    """
    print("-> A tentar ligar à API do Unsplash...")

    # 1. Verificar se a chave está disponível
    if not API_KEY:
        print("ERRO: A variável de ambiente 'UNSPLASH_ACCESS_KEY' não está definida.")
        print("Por favor, obtenha a sua chave no Unsplash e defina-a.")
        return None, None
    
    # Cabeçalhos de autenticação
    headers = {
        'Authorization': f'Client-ID {API_KEY}'
    }

    # Parâmetros da requisição:
    params = {
        'orientation': 'landscape', # Pedir fotos na orientação paisagem
        'query': 'nature,city,abstract' # (Opcional) Pode filtrar por tópicos, se quiser
    }
    
    try:
        # Fazer a requisição HTTP GET
        response = requests.get(UNSPLASH_API_URL, headers=headers, params=params)
        response.raise_for_status() # Lança um erro se o código HTTP for 4xx ou 5xx
        
        data = response.json()
        
        # O Unsplash devolve o URL de alta resolução na chave 'urls'
        # 'full' é uma boa opção; 'raw' é a mais alta resolução mas pode ser muito grande.
        image_url = data['urls']['full']
        
        # O título (caption) pode vir em diferentes formatos. Usamos a descrição ou um placeholder.
        title = data.get('alt_description') or data.get('description') or "Unsplash Photo"
        
        # Limpar o título, caso seja muito longo
        if len(title) > 50:
             title = title[:50] + "..."

        print(f"-> Imagem obtida com sucesso: '{title}'")
        return image_url, title
            
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            print("ERRO 403: Chave de API inválida ou limite de requisições atingido. Verifique a sua chave.")
        else:
            print(f"ERRO HTTP: Falha na ligação. Detalhe: {e}")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"ERRO GERAL: Falha na requisição. Detalhe: {e}")
        return None, None


def download_image(url, title):
    """
    Faz o download da imagem do URL especificado, guarda-a localmente
    e devolve o caminho do ficheiro guardado. (Função anterior, mantida)
    """
    if not os.path.exists(DOWNLOAD_DIR): 
        os.makedirs(DOWNLOAD_DIR)

    today = datetime.date.today().strftime("%Y-%m-%d")
    # Limpa o título para usar como parte do nome do ficheiro (ex: substitui espaços por '_')
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
    filename = f"{DOWNLOAD_DIR}/{today}_{safe_title.replace(' ', '_')}.jpg"
    
    print(f"-> A descarregar imagem para: {filename}")
    
    try:
        img_response = requests.get(url, stream=True)
        img_response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in img_response.iter_content(1024):
                f.write(chunk)
                
        print("-> Download concluído.")
        return filename
        
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Não foi possível descarregar a imagem do URL. Detalhe: {e}")
        return None


def main():
    """Função principal que orquestra os passos."""
    image_url, image_title = get_image_url()
    
    if image_url:
        local_path = download_image(image_url, image_title) 
        
        if local_path:
            print(f"Caminho do ficheiro guardado: {local_path}")
       
    print("\nFim do Passo 2 (Unsplash).")

if __name__ == "__main__":
    main()
