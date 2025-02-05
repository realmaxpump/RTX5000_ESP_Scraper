import subprocess
import sys
import datetime

# Lista de dependencias necesarias (mapeo de nombres para instalación e importación)
required_packages = {
    "pygame": "pygame",
    "selenium": "selenium",
    "webdriver_manager.chrome": "ChromeDriverManager",
    "bs4": "BeautifulSoup"
}

# Función para instalar e importar los paquetes
def install_and_import(packages):
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)  # Intentar importar el módulo
        except ImportError:
            print(f"📦 Instalando {package_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            __import__(import_name)  # Intentar importar el módulo (falla a veces)

# Instalar e importar librerías
install_and_import(required_packages)

# Hard import
import re
import time
import pygame
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

print("✅ Todas las dependencias han sido instaladas e importadas correctamente.")

# Diccionario de URLs y términos
urls_with_terms = {
    "https://www.appinformatica.com/componentes-de-ordenador/tarjetas-graficas?initialMap=c,c&initialQuery=componentes-de-ordenador/tarjetas-graficas&map=category-1,category-2,procesador-grafico&query=/componentes-de-ordenador/tarjetas-graficas/geforce-rtx-5080&searchState": ["Añadir"],
    "https://www.asusbymacman.es/tarjetas-graficas-nvidia-48?q=Series-GeForce+RTX+5080+Series-GeForce+RTX+5090+Series": ["Añadir a la cesta"],
    "https://www.beep.es/componentes-de-ordenador/tarjetas-graficas?initialMap=c,c&initialQuery=componentes-de-ordenador/tarjetas-graficas&map=category-1,category-2,procesador-grafico&query=/componentes-de-ordenador/tarjetas-graficas/geforce-rtx-5080": ["AÑADIR"],
    "https://www.beep.es/componentes-de-ordenador/tarjetas-graficas?initialMap=c,c&initialQuery=componentes-de-ordenador/tarjetas-graficas&map=category-1,category-2,procesador-grafico&query=/componentes-de-ordenador/tarjetas-graficas/geforce-rtx-5090": ["AÑADIR"],
    "https://www.caseking.es/componentes/tarjetas-graficas/nvidia/geforce-rtx-5080": ["Pocas unidades"],
    "https://www.caseking.es/componentes/tarjetas-graficas/nvidia/geforce-rtx-5090": ["Pocas unidades"],
    #"https://www.coolmod.com/tarjetas-graficas/serie-rtx-5090/serie-rtx-5080/": ["Añadir"],
    "https://www.ldlc.com/es-es/informatica/piezas-de-informatica/tarjeta-grafica/c4684/+fv121-126519,126520.html": ["DISPONIBLE"],
    "https://lifeinformatica.com/nvidia-geforce-rtx-serie-50/": ["Añadir al carrito"],
    "https://marketplace.nvidia.com/es-es/consumer/graphics-cards/?locale=es-es&page=1&limit=12&gpu=RTX%205080,RTX%205090&gpu_filter=RTX%205090~8,RTX%205080~2,RTX%204070%20Ti%20SUPER~6,RTX%204070%20Ti~4,RTX%204060%20Ti~3,RTX%204070%20SUPER~4,RTX%204070~4,RTX%204060~22,RTX%203080~1,RTX%203070%20Ti~1,RTX%203060%20Ti~1,RTX%203060~6,GTX%201650~1": ["Comprar Ahora"],
    "https://www.neobyte.es/tarjetas-graficas-nvidia-149?q=Grafica-NVIDIA+RTX+Serie+5000": ["Añadir al carrito"],
    "https://www.pccomponentes.com/tarjeta-grafica-asus-rog-astral-geforce-rtx-5080-oc-16gb-gddr7-reflex-2-rtx-ai-dlss4": ["Añadir al carrito"],
    "https://www.pccomponentes.com/tarjeta-grafica-asus-prime-geforce-rtx-5080-16gb-gddr7-reflex-2-rtx-ai-dlss4": ["Añadir al carrito"],
    "https://www.pccomponentes.com/tarjeta-grafica-msi-geforce-rtx-5080-vanguard-soc-launch-edition-16gb-gddr7-reflex-2-rtx-ai-dlss4": ["Añadir al carrito"],
    "https://www.pccomponentes.com/tarjeta-grafica-msi-geforce-rtx-5080-gaming-trio-oc-16gb-gddr7-reflex-2-rtx-ai-dlss4": ["Añadir al carrito"],
    "https://www.pccomponentes.com/tarjeta-grafica-gigabyte-geforce-rtx-5080-gaming-oc-16gb-gddr7-reflex-2-rtx-ai-dlss4": ["Añadir al carrito"],
    "https://www.pccomponentes.com/tarjeta-grafica-gigabyte-geforce-rtx-5080-windforce-oc-sff-16gb-gddr7-reflex-2-rtx-ai-dlss4": ["Añadir al carrito"],
    "https://www.pccomponentes.com/tarjeta-grafica-pny-geforce-rtx-5090-argb-overclocked-triple-fan-32gb-gddr7-reflex-2-rtx-ai-dlss4": ["Añadir al carrito"],
    "https://www.pccomponentes.com/tarjeta-grafica-asus-rog-astral-geforce-rtx-5090-oc-32gb-gddr7-reflex-2-rtx-ai-dlss4": ["Añadir al carrito"],
    "https://www.pccomponentes.com/tarjeta-grafica-msi-geforce-rtx-5090-suprim-soc-32gb-gddr7-reflex-2-rtx-ai-dlss4": ["Añadir al carrito"],
    "https://www.pccomponentes.com/tarjeta-grafica-asus-tuf-gaming-geforce-rtx-5090-oc-32gb-gddr7-reflex-2-rtx-ai-dlss4": ["Añadir al carrito"],
    "https://www.pccomponentes.com/tarjeta-grafica-asus-tuf-gaming-geforce-rtx-5090-32gb-gddr7-reflex-2-rtx-ai-dlss4": ["Añadir al carrito"],
    #"https://tienda.redcomputer.es/tarjetas-graficas-nvidia-rtx-10000020?q=Modelo+Gr%C3%A1fica-Nvidia+Geforce+RTX+5080-Nvidia+Geforce+RTX+5090": ["Comprar"],
    "https://wipoid.com/componentes/tarjetas-graficas/tarjetas-graficas-nvidia/?page=2&q=NVIDIA+Series-RTX+5080-RTX+5090": ["Añadir al carrito"],
    "https://wipoid.com/componentes/tarjetas-graficas/tarjetas-graficas-nvidia/?q=NVIDIA+Series-RTX+5080-RTX+5090": ["Añadir al carrito"],
    "https://es-store.msi.com/collections/tarjetas-graficas-nvidia-rtx-5080?sort_by=price-descending&filter.p.m.custom.grafica=GeForce+GTX+5080": ["Añadir al carrito"],
    "https://es-store.msi.com/collections/tarjetas-graficas-nvidia-rtx-5090?sort_by=price-descending&filter.p.m.custom.grafica=GeForce+GTX+5090": ["Añadir al carrito"],
}

def log_product_found(url):
    """Log the URL and current local time when a product is found."""
    with open("series_50_disponibles.txt", "a") as file:
        file.write(f"URL: {url} - Found at {current_time()}\n")

def current_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return current_time

def check_availability(url, search_terms):
    """Verifica la disponibilidad de las tarjetas gráficas en la página, ignorando header, footer, scripts y metadatos."""
    try:
        driver.get(url)  # Intentar cargar la página con timeout de 15 segundos

        # Esperar hasta que la página cargue completamente (máximo 10 segundos)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Intentar extraer solo el contenido dentro de <main> o elementos visibles
        page_content = ''
        try:
            page_element = driver.find_element(By.TAG_NAME, "main")
            page_content = page_element.get_attribute("innerHTML")
        except:
            # Si no hay <main>, extraer contenido de <body> excluyendo header, footer, scripts y metadatos
            body_element = driver.find_element(By.TAG_NAME, "body")
            body_html = body_element.get_attribute("innerHTML")

            # Eliminar todas las etiquetas no visibles (scripts, estilos, metadatos, etc.)
            for tag in ["header", "footer", "script", "style", "meta"]:
                elements = driver.find_elements(By.TAG_NAME, tag)
                for element in elements:
                    body_html = body_html.replace(element.get_attribute("outerHTML"), "")

            # Solo mantendremos el texto visible en el HTML
            page_content = body_html

        # Utilizamos BeautifulSoup para limpiar y extraer solo el texto visible
        soup = BeautifulSoup(page_content, 'html.parser')

        # Obtener el texto visible (sin etiquetas de estilo, script, etc.)
        visible_text = ' '.join(soup.stripped_strings)

        # Expresión regular para buscar los textos sin distinguir mayúsculas/minúsculas
        found = False
        for term in search_terms:
            if re.search(rf"\b{re.escape(term)}\b", visible_text, re.IGNORECASE):
                found = True
                break

        if found:
            money.play()
            log_product_found(url)
            print(f"💸💸💸💸 Producto disponible en: {url} 💸💸💸💸")
        else:
            print(f"❌ Producto NO disponible en: {url}")

    except Exception as e:
        print(f"⚠️ Error al procesar {url}")

#####################################
########### Execution ###############
#####################################

# Configuración de Selenium con opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--enable-unsafe-webgl")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--use-gl=swiftshader")

# Inicializar WebDriver
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(15)  # Timeout de carga de página: 15 segundos
except Exception as e:
    print(f"❌ Error al iniciar WebDriver: {e}")
    exit()

pygame.init()
money = pygame.mixer.Sound('src/sounds/found.mp3')

print(f"\n⚙️ Iniciando búsqueda de disponibilidad... ⚙️\n")

# Loop infinito para revisar cada página periódicamente
try:
    while True:
        for url, search_terms in urls_with_terms.items():
            check_availability(url, search_terms)

        print("\n🔄 Esperando antes de la próxima revisión... 🔄\n")
        time.sleep(5)

except KeyboardInterrupt:
    print("\n❌ Búsqueda detenida manualmente.")
    driver.quit()
