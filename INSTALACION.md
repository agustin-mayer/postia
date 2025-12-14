# Guía de Instalación - Postia Agent

## 🐍 Instalar Python

### Paso 1: Descargar Python
1. Ve a [python.org/downloads](https://www.python.org/downloads/)
2. Descarga Python 3.10 o superior (recomendado: Python 3.11 o 3.12)

### Paso 2: Instalar Python
1. Ejecuta el instalador descargado
2. **MUY IMPORTANTE:** Marca la casilla "Add Python to PATH" ✅
3. Haz clic en "Install Now"
4. Espera a que termine la instalación

### Paso 3: Verificar la Instalación
Abre una nueva ventana de PowerShell o CMD y ejecuta:
```bash
python --version
```

Deberías ver algo como: `Python 3.11.x`

## 🚀 Ejecutar Postia Agent

Una vez Python esté instalado:

1. Cierra cualquier ventana de terminal que tengas abierta
2. Haz doble clic en `Iniciar_Postia_Agent.bat`
3. La primera vez tomará unos minutos porque:
   - Creará un entorno virtual
   - Instalará todas las dependencias necesarias
4. Las siguientes veces iniciará mucho más rápido

## 📝 Notas

- El servidor correrá en: `http://127.0.0.1:5050`
- El token de autenticación está definido en el archivo `.bat`
- Para detener el servidor, presiona `Ctrl+C` en la ventana de la consola

## ❓ Problemas Comunes

### "Python no está en el PATH"
- Reinstala Python y asegúrate de marcar "Add Python to PATH"
- O agrega Python manualmente al PATH del sistema

### "Error al instalar dependencias"
- Verifica tu conexión a internet
- Intenta ejecutar manualmente: `pip install -r requirements.txt`

### "Chrome driver error"
- Asegúrate de tener Google Chrome instalado
- El script descargará automáticamente el driver correcto
