# 🎧 crear_spotify_bot

Bot avanzado en Python para la creación automática de cuentas en Spotify, con manejo de errores, generación de nombres realistas, limpieza de cookies y resolución automática de CAPTCHAs mediante la API de 2Captcha.

---

## 🧠 Funcionalidades

✅ Registro automatizado en la página de Spotify  
✅ Control de errores detallado y robusto  
✅ Integración con 2Captcha para resolver CAPTCHA invisibles  
✅ Generación automática de nombres con `Faker`  
✅ Limpieza de cookies tras cada cuenta para evitar detección  
✅ Compatible con IPROXY (opcional, aún no implementado)  
✅ Soporte para Excel (`correos_spotify.xlsx`) para leer cuentas

---

## 📦 Estructura de archivos


---

## ⚙️ Requisitos

- Python 3.10 o superior  
- Google Chrome instalado  
- Paquetes Python:
  ```bash
  pip install selenium pandas requests faker openpyxl
