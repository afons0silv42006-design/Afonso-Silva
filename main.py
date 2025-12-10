import requests
import datetime
import os
import ctypes # Para Windows
import subprocess # Para macOS/Linux
import platform # Para detetar o Sistema Operativo (OS)
from PIL import Image, ImageDraw, ImageFont # Para edição de imagem

#Configuração de Acesso e Variáveis

# A chave será lida da variável de ambiente.
# Ex: export UNSPLASH_ACCESS_KEY="sua_chave_de_acesso"
API_KEY = os.environ.get('UNSPLASH_ACCESS_KEY') 

UNSPLASH_API_URL = "https://api.unsplash.com/photos/random"
DOWNLOAD_DIR = "wallpapers" 

# Configuração da Edição de Imagem
FONT_PATH = "arial.ttf"  # Deve ter este ficheiro na pasta, ou use 'ImageFont.load_default()'
FONT_SIZE = 40
TEXT_COLOR = (255, 255, 255) # Branco (RGB)


def get_image_url():
    """
    Liga-se à API do Unsplash para obter uma foto aleatória de alta definição.
    Devolve (image_url, title) ou (None, None) em caso de falha.
    """
    print("-> A tentar ligar à API do Unsplash...")

    if not API_KEY:
        print("ERRO: A variável de ambiente 'UNSPLASH_ACCESS_KEY' não está definida.")
        print("Por favor, defina a variável no Terminal antes de correr o script.")
        return None, None
    
    headers = {
        'Authorization': f'Client-ID {API_KEY}'
    }

    params = {
        'orientation': 'landscape',
        'query': 'nature,city,abstract'
    }
    
    try:
        response = requests.get(UNSPLASH_API_URL, headers=headers, params=params)
        response.raise_for_status() 
        
        data = response.json()
        
        image_url = data['urls']['full']
        title = data.get('alt_description') or data.get('description') or "Unsplash Photo"
        
        if len(title) > 50:
             title = title[:50] + "..."

        print(f"-> Imagem obtida com sucesso: '{title}'")
        return image_url, title
            
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            print("ERRO 403: Chave de API inválida ou limite de requisições atingido.")
        else:
            print(f"ERRO HTTP: Falha na ligação. Detalhe: {e}")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"ERRO GERAL: Falha na requisição. Detalhe: {e}")
        return None, None


def download_image(url, title):
    """
    Faz o download da imagem e guarda-a localmente na pasta 'wallpapers'.
    """
    
    # Garantir que a pasta de destino existe
    if not os.path.exists(DOWNLOAD_DIR): 
        os.makedirs(DOWNLOAD_DIR)

    today = datetime.date.today().strftime("%Y-%m-%d")
    # Limpa o título para criar um nome de ficheiro seguro
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


def process_image(file_path, text_to_add=None):
    """
    Abre a imagem descarregada, adiciona texto formatado e guarda a versão final.
    """
    print("-> A processar imagem e adicionar texto...")
    
    try:
        img = Image.open(file_path)
    except Exception as e:
        print(f"ERRO: Não foi possível abrir a imagem em {file_path}. Detalhe: {e}")
        return None
    
    if text_to_add is None:
        return file_path
    
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE) 
    except IOError:
        print(f"Aviso: Não foi possível carregar a fonte '{FONT_PATH}'. A usar a fonte default.")
        font = ImageFont.load_default()
        
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Medir o tamanho do texto para calcular a posição
    bbox = draw.textbbox((0, 0), text_to_add, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Margem a partir do canto inferior direito
    MARGIN = 30
    position = (width - text_w - MARGIN, height - text_h - MARGIN)
    
    # Desenhar a sombra ligeiramente deslocada
    shadow_color = (0, 0, 0) # Preto
    draw.text((position[0] + 2, position[1] + 2), text_to_add, font=font, fill=shadow_color)
    
    # Desenhar o texto principal (branco)
    draw.text(position, text_to_add, font=font, fill=TEXT_COLOR)

    # Guardar a imagem processada (Substituímos o original)
    img.save(file_path)
    print("-> Texto adicionado e imagem guardada.")
    return file_path


def set_wallpaper(image_path):
    """
    Define o ficheiro especificado como o fundo de ecrã, dependendo do OS.
    """
    print("-> A definir a nova imagem como Wallpaper...")
    
    abs_path = os.path.abspath(image_path)
    
    os_name = os.name
    
    try:
        if os_name == 'nt' or os.getenv('OSTYPE') == 'msys': # Windows (nt ou MINGW64)
            # ctypes para o Windows API: Define o wallpaper
            # SPI_SETDESKWALLPAPER = 20
            ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
            print("SUCESSO: Wallpaper definido no Windows.")
        
        elif os_name == 'posix': # Linux/macOS
            
            if 'Darwin' in platform.system(): # macOS
                script = f"""
                tell application "Finder"
                    set desktop picture to POSIX file "{abs_path}"
                end tell
                """
                subprocess.Popen(['osascript', '-e', script])
                print("SUCESSO: Wallpaper definido no macOS.")
                
            else: # Linux (Geral)
                # Tenta primeiro GNOME (o mais comum)
                subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', f'file://{abs_path}'])
                # Tenta KDE
                subprocess.run(['qdbus', 'org.kde.plasma-active.desktopapp', '/PlasmaShell', 'setWallpaper', abs_path])
                print("SUCESSO: Tentativa de definir Wallpaper em Linux (GNOME/KDE).")
                
        else:
            print("AVISO: Sistema operativo não suportado para definição automática.")
            return False
            
        return True
        
    except Exception as e:
        print(f"ERRO: Falha ao definir o wallpaper. Detalhe: {e}")
        return False


def main():
    """Função principal que orquestra os passos."""
    
    # 1. Obter a URL da Imagem
    image_url, image_title = get_image_url()
    
    if image_url:
        # 2. Descarregar a Imagem
        local_path = download_image(image_url, image_title) 
        
        if local_path:
            # 3. Processar a Imagem (Adicionar Data)
            current_time_str = datetime.datetime.now().strftime("%A, %d de %B de %Y - %H:%M")
            processed_path = process_image(local_path, current_time_str)
            
            if processed_path:
                print(f"Imagem final pronta em: {processed_path}")
                
                # 4. Definir como Wallpaper
                set_wallpaper(processed_path) 
        
    print("\nFIM: Projeto Concluído!")

if __name__ == "__main__":
    main()
