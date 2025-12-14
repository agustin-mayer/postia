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

AGENT_TOKEN = os.getenv("AGENT_TOKEN", "changeme")


# Dominios permitidos (tu Bendia en producción + localhost para pruebas)
ALLOWED_ORIGINS = [
    "http://127.0.0.1:8010",
    "http://localhost:8010",
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
    # 👇 Dejamos que webdriver-manager detecte la versión automáticamente
    return Service(ChromeDriverManager().install())


def launch_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222")

    # ⚙️ Usá un perfil dedicado que no se use en tu Chrome normal
    # Crear el directorio del perfil si no existe
    profile_dir = os.path.join(
        os.getenv("LOCALAPPDATA", ""), 
        "Google", "Chrome", "User Data", "PostiaProfile"
    )
    os.makedirs(profile_dir, exist_ok=True)
    options.add_argument(f"user-data-dir={profile_dir}")

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


    
    print(f"\n{'='*60}")
    print(f"[INICIO] Nueva publicación solicitada")
    print(f"  Título: {payload.titulo}")
    print(f"  Precio: {payload.precio}")
    print(f"  Categoría: {payload.categoria}")
    print(f"  Estado: {payload.estado}")
    print(f"  Descripción: {payload.descripcion[:50]}..." if len(payload.descripcion) > 50 else f"  Descripción: {payload.descripcion}")
    print(f"{'='*60}\n")

    driver = launch_driver()
    try:
        print("[STEP 1] Navegando a Facebook Marketplace...")
        driver.get("https://www.facebook.com/marketplace/create/item")

        print("[STEP 2] Esperando que cargue la página...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(1)  # Espera adicional para carga completa
        


        # ====== Capturar todos los inputs visibles ======
        print("[STEP 3] Buscando campos de entrada...")
        try:
            inputs = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, '//input[@type="text"]'))
            )
            print(f"[DEBUG] ✅ Inputs detectados: {len(inputs)}")
            
            # Mostrar información de cada input
            for i, inp in enumerate(inputs):
                try:
                    placeholder = inp.get_attribute("placeholder") or "Sin placeholder"
                    aria_label = inp.get_attribute("aria-label") or "Sin aria-label"
                    visible = inp.is_displayed()
                    print(f"  Input {i}: placeholder='{placeholder}', aria-label='{aria_label}', visible={visible}")
                except Exception as e:
                    print(f"  Input {i}: Error al obtener info - {e}")
        except Exception as e:
            print(f"[ERROR] ❌ No se encontraron inputs: {e}")
            raise Exception(f"No se detectaron campos de entrada.")

        if len(inputs) < 2:
            raise Exception(f"Solo se detectaron {len(inputs)} inputs, se necesitan al menos 2")

        titulo_input = inputs[0]
        precio_input = inputs[1]

        # Completar campos básicos
        print(f"[STEP 4] Completando título: '{payload.titulo}'")
        try:
            titulo_input.clear()
            titulo_input.send_keys(payload.titulo)
            time.sleep(0.1)
            valor_actual = titulo_input.get_attribute("value")
            print(f"[DEBUG] ✅ Título ingresado. Valor actual: '{valor_actual}'")
        except Exception as e:
            print(f"[ERROR] ❌ Error al ingresar título: {e}")
            raise

        print(f"[STEP 5] Completando precio: '{payload.precio}'")
        try:
            precio_input.clear()
            precio_input.send_keys(payload.precio)
            time.sleep(0.1)
            valor_actual = precio_input.get_attribute("value")
            print(f"[DEBUG] ✅ Precio ingresado. Valor actual: '{valor_actual}'")
        except Exception as e:
            print(f"[ERROR] ❌ Error al ingresar precio: {e}")
            raise



        # ====== Scroll hasta el final del formulario ======
        print("[STEP 6] Haciendo scroll...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)

        # ====== Categoría ======
        print(f"[STEP 7] Seleccionando categoría: '{payload.categoria}'")
        try:
            categoria_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[.//text()[contains(., "Categoría")]]/following-sibling::div'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", categoria_div)
            time.sleep(0.1)
            driver.execute_script("arguments[0].click();", categoria_div)
            time.sleep(0.1)
            print("[DEBUG] ✅ Dropdown de categoría abierto")

            opcion = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(), "{payload.categoria}")]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", opcion)
            time.sleep(0.1)
            driver.execute_script("arguments[0].click();", opcion)
            print(f"[DEBUG] ✅ Categoría '{payload.categoria}' seleccionada")
        except Exception as e:
            print(f"[WARN] ⚠️ No se pudo seleccionar categoría: {e}")



        # ====== Estado ======
        print(f"[STEP 8] Seleccionando estado: '{payload.estado}'")
        try:
            estado_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[.//text()[contains(., "Estado")]]/following-sibling::div'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", estado_div)
            time.sleep(0.1)
            driver.execute_script("arguments[0].click();", estado_div)
            time.sleep(0.1)
            print("[DEBUG] ✅ Dropdown de estado abierto")

            opcion_estado = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(), "{payload.estado}")]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", opcion_estado)
            time.sleep(0.1)
            driver.execute_script("arguments[0].click();", opcion_estado)
            print(f"[DEBUG] ✅ Estado '{payload.estado}' seleccionado")
        except Exception as e:
            print(f"[WARN] ⚠️ No se pudo seleccionar estado: {e}")

        # ====== Descripción ======
        print(f"[STEP 9] Completando descripción...")
        try:
            desc_area = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//textarea'))
            )
            desc_area.clear()
            desc_area.send_keys(payload.descripcion)
            time.sleep(0.1)
            print(f"[DEBUG] ✅ Descripción ingresada: '{payload.descripcion[:50]}...'")
        except Exception as e:
            print(f"[WARN] ⚠️ Error al ingresar descripción: {e}")
        

        
        # ====== Scroll profundo hasta la sección de entrega ======
        print("[STEP 10] Desplazando hasta la sección de entrega...")
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            contenedores = driver.find_elements(By.XPATH, '//div[@role="main" or @aria-label="Marketplace" or @class]')
            for c in contenedores:
                try:
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", c)
                except Exception:
                    continue
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)
        except Exception as e:
            print(f"[WARN] ⚠️ No se pudo hacer scroll profundo: {e}")

        # ====== Marcar checkboxes de entrega ======
        print("[STEP 11] Marcando opciones de entrega...")
        def marcar_checkbox(texto):
            try:
                bloque = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//span[contains(., "{texto}")]/ancestor::div[@role="checkbox" or @aria-checked]'))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bloque)
                time.sleep(0.1)
                estado = bloque.get_attribute("aria-checked")
                if estado != "true":
                    driver.execute_script("arguments[0].click();", bloque)
                    print(f"[DEBUG] ✅ '{texto}' marcado correctamente")
                else:
                    print(f"[DEBUG] ℹ️ '{texto}' ya estaba marcado")
            except Exception as e:
                print(f"[WARN] ⚠️ No se pudo marcar '{texto}': {e}")

        marcar_checkbox("Retiro en la puerta")
        marcar_checkbox("Entrega en la puerta")

        time.sleep(0.1)
        
        print("[DEBUG] ✅ Formulario completado correctamente")

        # ====== Guardar borrador y salir ======
        print("[STEP 12] Intentando guardar borrador...")
        try:
            guardar_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//span[normalize-space(text())="Guardar borrador" or normalize-space(.)="Guardar borrador"]/ancestor::div[@role="button" or @tabindex]'
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", guardar_btn)
            time.sleep(0.1)
            driver.execute_script("arguments[0].click();", guardar_btn)
            print("[DEBUG] ✅ Botón 'Guardar borrador' clickeado")
            time.sleep(1)
        except Exception as e:
            print(f"[WARN] ⚠️ No se pudo guardar borrador: {e}")

        # ====== Finalizar ======
        print(f"\n{'='*60}")
        print("[FINALIZADO] ✅ Todo el proceso completado exitosamente")
        print(f"{'='*60}\n")
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
            print("[CLOSE] Navegador cerrado correctamente")
        except Exception:
            pass