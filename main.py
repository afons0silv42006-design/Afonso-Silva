import requests
import datetime
import os

# URL da API da NASA APOD

NASA_API_URL = "https://api.nasa.gov/planetary/apod"

API_KEY = "DEMO_KEY"

def get_image_url():
    """
    Liga-se à API da NASA para obter a 'Astronomy Picture of the Day' (APOD).
    Devolve o URL da imagem de alta definição (HD) ou None em caso de falha.
    """
    print("-> A tentar ligar à API da NASA...")

# Parâmetros da requisição: pedimos a imagem de hoje e a chave de API
    params = {
        'api_key': API_KEY,
        'hd': 'True' # Pedir a versão de alta definição
    }
    
    try:
        # 1. Fazer a requisição HTTP GET
        response = requests.get(NASA_API_URL, params=params)
        
        # 2. Verificar se a requisição foi bem-sucedida (código 200)
        response.raise_for_status() 
        
        data = response.json()
        
        # 3. Verificar o tipo de conteúdo (a NASA por vezes mostra vídeos)
        if data.get('media_type') == 'image':
            image_url = data.get('hdurl', data.get('url')) # Preferir hdurl
            title = data.get('title', 'NASA Picture')
            print(f"-> Imagem obtida com sucesso: '{title}'")
            return image_url, title
        else:
            print(f"-> O conteúdo de hoje não é uma imagem ({data.get('media_type')}). A ignorar.")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha na ligação à API ou na resposta. Detalhe: {e}")
        return None, None

def main():
    """Função principal que orquestra os passos."""
    image_url, image_title = get_image_url()
    
    if image_url:
        print(f"URL da imagem para download: {image_url}")
        # O próximo passo será descarregar esta imagem!
        # download_image(image_url, image_title) 
        
    print("\nFim do Passo 1.")

if __name__ == "__main__":
    main()
