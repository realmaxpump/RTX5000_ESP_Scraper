import sys
import subprocess
import platform
import requests
import time
from datetime import datetime
import json
import re

required_packages = {
    "setuptools": "setuptools",
    "selenium": "selenium",
    "beautifulsoup4": "bs4",
    "undetected_chromedriver": "undetected_chromedriver",
    "winsound": "winsound",
    "brotli": "brotli"
}
#####################################
########### Config ###############
#####################################

# Winsound
ALARM_FREQ = 2000  # Set Frequency To 2500 Hertz
ALARM_DURATION = 800  # Set Duration To 1000 ms == 1 second

# Telegram
USE_TELEGRAM = False
TELEGRAM_TOKEN = ""
TELEGRAM_CHAT_ID = ""

# Rutas de los diccionarios
TARGETS_FILE = "src/data/targets.json"
TEST_TARGETS_FILE = "src/data/test_targets.json"

# Tiempo máximo de espera por página
TIMEOUT_THRESHOLD = 7

# Constants
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'  # Para restaurar el color predeterminado

# Requests config
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Accept-Language": "en-US,en;q=0.8,es;q=0.6",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
    "DNT": "1",  # Do Not Track activado
    "Upgrade-Insecure-Requests": "1"
}

# Functions
def log_product_found(url):
    """Log the URL and current local time when a product is found."""
    with open("series_50_disponibles.txt", "a") as file:
        file.write(f"URL: {url} - Found at {current_time()}\n")

def current_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return current_time

def print_separator(width=100):
    print('\n' + '='.center(width, '=') + '\n')

def install_packages(packages):
    """Instala paquetes si no están disponibles."""
    try:
        import setuptools  # Verifica si setuptools ya está disponible
    except ImportError:
        print("📦 Reconstituyendo distutils y setuptools...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", "setuptools"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    for package, module in packages.items():
        try:
            __import__(module)
        except ImportError:
            print(f"📦 Instalando {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", package],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                __import__(module)  # Intentar importar de nuevo tras la instalación
            except ImportError:
                print(f"❌ No se pudo instalar correctamente {package}. Reintente manualmente.")
                exit(1)  # Detener ejecución si falla

def show_menu():
    print_separator()
    print("🎯 Selecciona una opción:")
    print("1️🔹 Empezar Búsqueda en modo silencioso (recomendado)")
    print("2️🔹 Empezar Búsqueda en modo gráfico")
    print("3️🔹 Modo Test de URLs")
    print("4️🔹 Salir")
    print(f"\n\tScript desarrollado por: {RED}RealMaxPump {RESET}")
    print("\thttps://github.com/realmaxpump")
    print_separator()

def load_urls_from_file(file):
    try:
        with open(file, "r", encoding="utf-8") as file:
            return json.load(file)  # Carga el archivo como un diccionario JSON
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error al cargar el archivo {file}: {e}")
        return {}

def get_chrome_version():
    """Obtiene la versión instalada de Chrome en Windows, Linux o macOS."""
    try:
        system = platform.system().lower()  # Obtener el sistema operativo

        if system == "windows":
            # Comando para obtener la versión de Chrome en Windows
            result = subprocess.run(
                ["reg", "query", "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon", "/v", "version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                # Extraer la versión de la salida del comando
                version = result.stdout.strip().split()[-1]
                return int(version.split(".")[0])  # Devolver solo el número principal (por ejemplo, 133)
            else:
                print("❌ No se pudo obtener la versión de Chrome en Windows.")
                return None

        elif system == "linux":
            # Comando para obtener la versión de Chrome en Linux
            result = subprocess.run(
                ["google-chrome", "--version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                # Extraer la versión de la salida del comando
                version = re.search(r"\d+\.\d+\.\d+", result.stdout.strip())
                if version:
                    return int(version.group().split(".")[0])  # Devolver solo el número principal
            else:
                print("❌ No se pudo obtener la versión de Chrome en Linux.")
                return None

        elif system == "darwin":  # macOS
            # Comando para obtener la versión de Chrome en macOS
            result = subprocess.run(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                # Extraer la versión de la salida del comando
                version = re.search(r"\d+\.\d+\.\d+", result.stdout.strip())
                if version:
                    return int(version.group().split(".")[0])  # Devolver solo el número principal
            else:
                print("❌ No se pudo obtener la versión de Chrome en macOS.")
                return None

        else:
            print(f"❌ Sistema operativo no compatible: {system}")
            return None

    except Exception as e:
        print(f"❌ Error al obtener la versión de Chrome: {e}")
        return None

def webdriver_start(mode):
    global driver
    try:
        print("🚀 Iniciando WebDriver...")

        # Configure Chrome options. Obfuscate identity to bypass variou antibot measures
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--enable-unsafe-webgl")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--use-gl=swiftshader")
        if mode == 1: chrome_options.add_argument("--headless=new")

        if chrome_version:
            print(f"✅ Versión de Chrome detectada: {chrome_version}")
            driver = uc.Chrome(version_main=chrome_version, use_subprocess=True, options=chrome_options)
        else:
            print("⚠️ No se pudo detectar la versión de Chrome. Intentando iniciar WebDriver de manera genérica...")
            driver = uc.Chrome(use_subprocess=True, options=chrome_options)

        driver.set_page_load_timeout(TIMEOUT_THRESHOLD)  # Timeout de carga de página
        driver.set_script_timeout(TIMEOUT_THRESHOLD)

        print("✅ WebDriver inicializado correctamente.")
        print_separator()

    except Exception as e:
        print(f"❌ Error al iniciar WebDriver: {e}")
        sys.exit(1)  # Detener el script si no se puede iniciar el WebDriver

def webdriver_restart():
    """Reinicia el WebDriver correctamente, asegurando que se cierre antes de volver a iniciar."""
    global driver
    print("🔄 Reiniciando WebDriver...")
    try:
        driver.quit()
        time.sleep(3)
    except Exception as e:
        print(f"⚠️ Aviso al cerrar WebDriver: {e}")
        exit()
    webdriver_start(mode)

def scrape_brute(url):
    """Verifica la disponibilidad de las tarjetas gráficas en la página, ignorando header, footer, scripts y metadatos."""
    try:
        driver.get(url)  # Intentar cargar la página con timeout de 15 segundos
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Esperar hasta que la página cargue completamente (máximo 10 segundos)
        WebDriverWait(driver, TIMEOUT_THRESHOLD).until(EC.presence_of_element_located((By.CSS_SELECTOR, "main, body")))
        try:
            page_element = driver.find_element(By.TAG_NAME, "main")
        except:
            # Si no hay <main>, extraer contenido de <body>
            page_element = driver.find_element(By.TAG_NAME, "body")

        # Eliminar elementos no deseados directamente del DOM
        tags_to_remove = ["header", "footer", "script", "style", "meta", "nav", "aside"]
        for tag in tags_to_remove:
            driver.execute_script(f"""
                    var elements = document.getElementsByTagName('{tag}');
                    while (elements[0]) {{
                        elements[0].parentNode.removeChild(elements[0]);
                    }}
                """)

        # Obtener el contenido filtrado
        page_content = page_element.get_attribute("innerHTML")

        # Utilizamos BeautifulSoup para limpiar y extraer solo el texto visible
        return BeautifulSoup(page_content, 'html.parser')

    except Exception as e:
        error_message = str(e).lower()
        if ("invalid session id" in error_message
                or "read timeout" in error_message):
            #               or "timed out receiving message from renderer" in error_message):
            print(f"⚠️ Error detectado: {error_message}")
            webdriver_restart()
            return None
        else:
            print(f"⚠️ Error inesperado en {url}: {e}")
            return None

def scrape_with_requests(url, selector=""):
    """Scrapea páginas usando requests y BeautifulSoup con manejo de compresión seguro."""
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=7)

        # Detectar si la respuesta está comprimida
        content_encoding = response.headers.get("Content-Encoding", "").lower()
        raw_content = response.content

        # Si el contenido empieza con '<', es HTML y no necesita descomprimir
        if raw_content[:2] == b'<!':
            html = raw_content.decode("utf-8", errors="ignore")
        elif content_encoding == "gzip":
            try:
                print(f"📌 Respuesta comprimida con GZIP en {url}. Descomprimiendo...")
                html = gzip.decompress(raw_content).decode("utf-8", errors="ignore")
            except OSError:
                print(f"❌ Error: El contenido de {url} no es realmente un archivo GZIP.")
                html = raw_content.decode("utf-8", errors="ignore")  # Leer sin descomprimir
        elif content_encoding == "br":
            try:
                print(f"📌 Respuesta comprimida con Brotli en {url}. Descomprimiendo...")
                html = brotli.decompress(raw_content).decode("utf-8", errors="ignore")
            except brotli.error:
                print(f"❌ Error: El contenido de {url} no es realmente Brotli.")
                html = raw_content.decode("utf-8", errors="ignore")  # Leer sin descomprimir
        else:
            html = raw_content.decode("utf-8", errors="ignore")  # Si no está comprimido, usarlo tal cual

        # Verificar si la respuesta es válida
        if "<html" not in html:
            print(f"❌ La respuesta de {url} no contiene HTML válido.")
            return None
        soup = BeautifulSoup(html, "html.parser")

        # Aplicar selector si está definido
        if selector:
            elements = soup.select(selector)
            if elements:
                # Si hay varios elementos, extraer el texto de cada uno
                return BeautifulSoup("\n".join(str(el) for el in elements), "html.parser")  # Retorna un nuevo `soup`
            else:
                # Si el producto no está disponible, no encuentra el selector en muchos casos
                return None
        return soup  # Retornar el contenido si no hay selector específico
    except requests.exceptions.RequestException as e:
        print(f"⚠️ No se pudo acceder a {url}: {e}")
        return None

def check_availability(url, search_terms, method, selector=""):
    """Verifica si un producto está disponible según el method y términos configurados."""
    global driver
    try:
        if method == "request":
            soup = scrape_with_requests(url, selector)
        elif method == "brute":
            soup = scrape_brute(url)
        else:
            print(f"⚠️ Método desconocido para {url}. Saltando...")
            return
        if soup:
            visible_text = ' '.join(soup.stripped_strings)
            found = any(re.search(rf"\b{re.escape(term)}\b", visible_text, re.IGNORECASE) for term in search_terms)

            if found:
                print(f"💸 Producto DISPONIBLE en: {url}")
                log_product_found(url)
                winsound.Beep(ALARM_FREQ, ALARM_DURATION)
                if USE_TELEGRAM:
                    try:
                        send_message_telegram(f"💸💸💸💸 STOCK DISPONIBLE  💸💸💸💸\n\n{url}")
                        print(f"✅ Notificado")
                    except Exception as e:
                        print(f"❌ Error al enviar mensaje a Telegram: {e}")
                    print_separator()
            else:
                short_url = url[:70] + "..." if len(url) > 70 else url
                print(f"❌ Producto NO disponible en: {short_url}")
        elif method == "request":
            short_url = url[:70] + "..." if len(url) > 70 else url
            print(f"❌ Producto NO disponible en: {short_url}")
        else:
            return  # Si el scraping falló, pasamos al siguiente
    except Exception as e:
        print(f"⚠️ Error en {url}")
        #print(f"⚠️ Error en {url}: {e}")

def send_message_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.get(url, params=params)

#####################################
########### Execution ###############
#####################################

# Instalar e importar librerías
install_packages(required_packages)

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import winsound

print("✅ Todas las dependencias han sido instaladas e importadas correctamente")

# Inicializar Alarma
if ALARM_FREQ and ALARM_DURATION:
    print("✅ 🚨Alarma🚨 preparada")
else:
    print(f"❌ No se ha podido inicializar la alarma")

#Inicializar Telegram
if USE_TELEGRAM:
    if not TELEGRAM_CHAT_ID:
        print("❌ 🤖Bot🤖 de Telegram no configurado")
    else:
        print(f"✅ 🤖Bot🤖 de Telegram iniciado correctamente. Chat ID encontrado: {TELEGRAM_CHAT_ID}")
else:
    print(f"❌ 🤖Bot🤖 de Telegram deshabilitado")

while True:
    show_menu()
    choice = input("🔹 Opción (1/2/3/4): ").strip()

    if choice == "1":
        mode = 1
        print("\n🚀 Iniciando búsqueda de disponibilidad silencioso...")
        urls_with_terms = load_urls_from_file(TARGETS_FILE)
        break
    elif choice == "2":
        mode = 2
        print("\n🛠️ Iniciando búsqueda de disponibilidad gráfico...")
        urls_with_terms = load_urls_from_file(TARGETS_FILE)
        break
    elif choice == "3":
        mode = 3
        print("\n🛠️ Iniciando Modo Test con URLs de prueba...")
        urls_with_terms = load_urls_from_file(TEST_TARGETS_FILE)
        break
    elif choice == "4":
        print("👋 ¡Espero que haya habido suerte!")
        sys.exit()
    else:
        print("❌ Opción inválida. Inténtalo de nuevo.")

# Detectar la versión de Chrome instalada
chrome_version = get_chrome_version()

# Inicializar WebDriver
webdriver_start(mode)

# Loop infinito para revisar cada página periódicamente
try:
    while True:
        for url, config in urls_with_terms.items():
            check_availability(url, config["terms"], config["method"], config.get("selector", ""))
        print("\n🔄 Esperando antes de la próxima revisión... 🔄\n")
        time.sleep(1)

except KeyboardInterrupt:
    print("\n❌ Búsqueda detenida manualmente.")
    try:
        driver.quit()
    except Exception as e:
        print(f"❌ Error al cerrar WebDriver: {e}")