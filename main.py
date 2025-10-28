import os
import time
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import os
AGENT_TOKEN = os.getenv("AGENT_TOKEN", "changeme")


# Dominios permitidos (tu Bendia en producción + localhost para pruebas)
ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    # Agregá tu dominio real de Bendia en producción, ej:
    "https://bendia.com.ar",
    "https://www.bendia.com.ar",
]

# Ruta a tu perfil de Chrome (para usar TU sesión)
# Ajustá al tuyo. Ejemplo Windows:
CHROME_USER_DATA_DIR = os.path.join(
    os.getenv("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "PostiaProfile"
)
# ========= APP =========
app = FastAPI(title="Postia Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PublicacionPayload(BaseModel):
    titulo: str
    precio: str
    descripcion: Optional[str] = ""
    categoria: str = "Electrónica e informática"  # exacto como aparece
    estado: str = "Nuevo"
    retiro_puerta: bool = True
    entrega_puerta: bool = True


def get_driver_service():
    # 👇 Forzamos la versión exacta de tu Chrome
    return Service(ChromeDriverManager(driver_version="141.0.7390.123").install())


def launch_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222")

    # ⚙️ Usá un perfil dedicado que no se use en tu Chrome normal
    options.add_argument(r"user-data-dir=C:\Users\Agustin\AppData\Local\Google\Chrome\User Data\PostiaProfile")

    driver = webdriver.Chrome(
        service=get_driver_service(),
        options=options
    )
    return driver


def click_by_text(driver, text_substring):
    el = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f'//*[contains(text(), "{text_substring}")]'))
    )
    driver.execute_script("arguments[0].click();", el)


@app.post("/publicar")
def publicar(payload: PublicacionPayload, x_agent_token: str = Header(default="")):
    if x_agent_token != AGENT_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")

    driver = launch_driver()
    try:
        driver.get("https://www.facebook.com/marketplace/create/item")

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(1)  # margen por carga perezosa

        # ====== Capturar todos los inputs visibles ======
        inputs = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, '//input[@type="text"]'))
        )
        print(f"[DEBUG] Inputs detectados: {len(inputs)}")

        # Facebook cambia nombres dinámicos; el orden actual es:
        # 0 = Título
        # 1 = Precio
        # (luego SKU, ubicación, etc.)

        if len(inputs) < 2:
            raise Exception("No se detectaron los campos de título y precio")

        titulo_input = inputs[0]
        precio_input = inputs[1]

        # Completar campos básicos
        titulo_input.clear()
        titulo_input.send_keys(payload.titulo)
        time.sleep(0.3)

        precio_input.clear()
        precio_input.send_keys(payload.precio)
        time.sleep(0.3)

                # ====== Scroll hasta el final del formulario ======
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.3)

        # ====== Categoría ======
        try:
            print("[INFO] Buscando dropdown de categoría...")
            categoria_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[.//text()[contains(., "Categoría")]]/following-sibling::div'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", categoria_div)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", categoria_div)
            time.sleep(0.3)

            opcion = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(), "{payload.categoria}")]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", opcion)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", opcion)
            print("[OK] Categoría seleccionada correctamente.")
        except Exception as e:
            print(f"[WARN] No se pudo seleccionar categoría: {e}")

        # ====== Estado ======
        try:
            print("[INFO] Buscando dropdown de estado...")
            estado_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[.//text()[contains(., "Estado")]]/following-sibling::div'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", estado_div)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", estado_div)
            time.sleep(0.3)

            opcion_estado = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(), "{payload.estado}")]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", opcion_estado)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", opcion_estado)
            print("[OK] Estado seleccionado correctamente.")
        except Exception as e:
            print(f"[WARN] No se pudo seleccionar estado: {e}")

        # ====== Descripción ======
        desc_area = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//textarea'))
        )
        desc_area.clear()
        desc_area.send_keys(payload.descripcion)
        time.sleep(0.3)
         # ====== Scroll profundo hasta la sección de entrega ======
        print("[INFO] Desplazando hasta la sección de entrega...")

        # Intentar varios métodos de scroll por compatibilidad
        try:
            # 1️⃣ Scroll global de la ventana
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


            # 2️⃣ Scroll interno del contenedor principal
            contenedores = driver.find_elements(By.XPATH, '//div[@role="main" or @aria-label="Marketplace" or @class]')
            for c in contenedores:
                try:
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", c)
                except Exception:
                    continue

            # 3️⃣ Pequeño scroll adicional por si todavía no aparece
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)
        except Exception as e:
            print(f"[WARN] No se pudo hacer scroll profundo: {e}")

        # ====== Marcar checkboxes de entrega ======
        def marcar_checkbox(texto):
            try:
                # Localizar el contenedor principal del texto (el bloque que contiene el icono, texto y el div clickeable)
                bloque = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//span[contains(., "{texto}")]/ancestor::div[@role="checkbox" or @aria-checked]'))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bloque)
                time.sleep(0.3)
                estado = bloque.get_attribute("aria-checked")
                if estado != "true":
                    driver.execute_script("arguments[0].click();", bloque)
                    print(f"[OK] {texto} marcado correctamente.")
                else:
                    print(f"[INFO] {texto} ya estaba marcado.")
            except Exception as e:
                print(f"[WARN] No se pudo marcar {texto}: {e}")

        marcar_checkbox("Retiro en la puerta")
        marcar_checkbox("Entrega en la puerta")

        time.sleep(0.3)
        print("[OK] Formulario completado correctamente.")

                # ====== Guardar borrador y salir ======
        try:
            print("[INFO] Intentando guardar borrador...")
            guardar_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//span[normalize-space(text())="Guardar borrador" or normalize-space(.)="Guardar borrador"]/ancestor::div[@role="button" or @tabindex]'
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", guardar_btn)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", guardar_btn)
            print("[OK] Botón 'Guardar borrador' clickeado.")


            time.sleep(3)
        except Exception as e:
            print(f"[WARN] No se pudo guardar borrador o salir: {e}")

        # ====== Finalizar ======
        print("[OK] Todo el proceso completado exitosamente.")
        return {"status": "ok", "message": "Formulario completado y guardado como borrador."}



    except Exception as e:
        try:
            driver.quit()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Error al completar formulario: {e}")
    
    finally:
        try:
            driver.quit()
            print("[CLOSE] Navegador cerrado correctamente.")
        except Exception:
            pass