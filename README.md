## 🧠 Postia

**Postia** es un agente local desarrollado en **Python + FastAPI + Selenium** que automatiza la carga de publicaciones en *Marketplace*, completando automáticamente los campos de un formulario web como título, precio, descripción, categoría, estado y opciones de entrega.

El objetivo de Postia es agilizar la creación de publicaciones desde datos externos (por ejemplo, productos ya registrados en tu sistema local) sin depender de tareas manuales repetitivas.

---

## 🚀 Características

- Interfaz **FastAPI** para recibir datos vía HTTP.
- Ejecución local del navegador **Google Chrome** mediante Selenium.
- Autocompletado de campos clave del formulario de publicación.
- Soporte para perfiles de usuario dedicados de Chrome (`PostiaProfile`).
- Guardado automático como **borrador**.
- Cierre automático del navegador al finalizar.

---

## ⚙️ Requisitos

- **Python 3.9+**
- **Google Chrome** instalado.
- **ChromeDriver** (se gestiona automáticamente con `webdriver-manager`).

---

## 🧩 Instalación

```bash
git clone https://github.com/tuusuario/postia.git
cd postia
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Ejecución
Podés iniciar Postia desde el archivo .bat incluido o manualmente:
```bash
Copiar código
python main.py
Por defecto se ejecuta en http://127.0.0.1:5050.
```
📦 Ejemplo de uso
Enviá una solicitud HTTP con los datos del producto:
```bash
Copiar código
POST http://127.0.0.1:5050/publicar
Header: X-Agent-Token: tu_token_secreto
Body (JSON):
{
  "titulo": "Cable de red 10m",
  "precio": "12000",
  "descripcion": "Cable de red de 10 metros, ideal para conectar router y PC.",
  "categoria": "Electrónica e informática",
  "estado": "Nuevo",
  "retiro_puerta": true,
  "entrega_puerta": true
}
```
El agente abrirá Chrome, completará el formulario y lo guardará como borrador.

## 🧠 Notas importantes
Postia no interactúa directamente con APIs externas. Solo automatiza formularios visibles mediante un navegador real.

La autenticación debe realizarse manualmente una vez por perfil (Postia usa PostiaProfile para mantener la sesión iniciada).

Si necesitás ejecutar varias cuentas, podés crear varios perfiles de Chrome (PostiaProfile1, PostiaProfile2, etc.).

## 🔒 Seguridad
No subas ni compartas la carpeta User Data (contiene tu sesión de Chrome).

El token del agente (AGENT_TOKEN) debe almacenarse en variables de entorno o un archivo .env local.

Evitá ejecutar el agente con permisos administrativos innecesarios.

## 🧾 Licencia
Este proyecto está disponible bajo la licencia MIT.
Podés usarlo, modificarlo y adaptarlo libremente, siempre que mantengas la atribución al autor original.

## 👨‍💻 Autor
Desarrollado por Agustín Mayer
Postia — Agente local para automatización de formularios Marketplace.