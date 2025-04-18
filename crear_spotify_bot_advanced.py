
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import logging
import json
import requests
from faker import Faker

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def cargar_configuracion(ruta_config):
    with open(ruta_config, "r") as f:
        return json.load(f)

config = cargar_configuracion("config.json")
EXCEL_PATH = config["excel_path"]
CHROME_DRIVER_PATH = config["chrome_driver_path"]
API_KEY_2CAPTCHA = config["api_key_2captcha"]
CANTIDAD_CUENTAS = config.get("cantidad_cuentas", 1)
USAR_PROXY = config.get("usar_proxy", False)
PROXY = config.get("proxy_config", {})
FAKER = Faker()

def configurar_driver(ruta_chromedriver):
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("user-agent=" + FAKER.user_agent())
    if USAR_PROXY:
        proxy_auth = f'{PROXY["usuario"]}:{PROXY["clave"]}@{PROXY["host"]}:{PROXY["port"]}'
        options.add_argument(f'--proxy-server=http://{proxy_auth}')
    service = webdriver.chrome.service.Service(ruta_chromedriver)
    return webdriver.Chrome(service=service, options=options)

def leer_excel(ruta):
    try:
        return pd.read_excel(ruta)
    except:
        return pd.DataFrame()

def guardar_excel(df, ruta):
    try:
        df.to_excel(ruta, index=False)
    except Exception as e:
        logging.error(f"Error guardando Excel: {e}")

def resolver_captcha(api_key, sitekey, url):
    try:
        r = requests.post("http://2captcha.com/in.php", data={
            "key": api_key,
            "method": "userrecaptcha",
            "googlekey": sitekey,
            "pageurl": url,
            "json": 1
        }).json()
        if r["status"] != 1:
            return None
        captcha_id = r["request"]
        for _ in range(30):
            time.sleep(5)
            r2 = requests.get(f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}&json=1").json()
            if r2["status"] == 1:
                return r2["request"]
        return None
    except:
        return None

def esperar_y_enviar_keys(wait, by, selector, value, max_intentos=3):
    for _ in range(max_intentos):
        try:
            campo = wait.until(EC.visibility_of_element_located((by, selector)))
            campo.send_keys(value)
            return True
        except:
            time.sleep(1)
    return False

def esperar_y_click(driver, wait, by, selector, max_intentos=3):
    for _ in range(max_intentos):
        try:
            boton = wait.until(EC.element_to_be_clickable((by, selector)))
            driver.execute_script("arguments[0].click();", boton)
            return True
        except:
            time.sleep(1)
    return False

def generar_nombre_usuario():
    return FAKER.user_name()

def limpiar_cookies(driver):
    driver.delete_all_cookies()

def crear_cuenta_spotify(driver, correo, clave):
    try:
        driver.get("https://www.spotify.com/pe/signup")
        wait = WebDriverWait(driver, 20)
        if "captcha" in driver.page_source:
            sitekey = driver.find_element(By.CLASS_NAME, "g-recaptcha").get_attribute("data-sitekey")
            token = resolver_captcha(API_KEY_2CAPTCHA, sitekey, driver.current_url)
            if not token:
                return None
            driver.execute_script("document.getElementById('g-recaptcha-response').innerHTML='%s';" % token)
        nombre_usuario = generar_nombre_usuario()
        esperar_y_enviar_keys(wait, By.ID, "email", correo)
        esperar_y_enviar_keys(wait, By.ID, "confirm", correo)
        esperar_y_enviar_keys(wait, By.ID, "password", clave)
        esperar_y_enviar_keys(wait, By.ID, "displayname", nombre_usuario)
        esperar_y_click(driver, wait, By.ID, "register-button-email-submit")
        try:
            wait.until(EC.url_contains("signup-complete"))
        except:
            pass
        return nombre_usuario
    except Exception as e:
        logging.error(f"Error en {correo}: {e}")
        return None

def main():
    df = leer_excel(EXCEL_PATH)
    if df.empty:
        logging.error("Excel vacío o no encontrado.")
        return
    driver = configurar_driver(CHROME_DRIVER_PATH)
    procesados = 0
    for index, row in df.iterrows():
        if row.get("usado") == "sí":
            continue
        correo, clave = row["correo"], row["clave"]
        nombre = crear_cuenta_spotify(driver, correo, clave)
        if nombre:
            df.loc[index, "usado"] = "sí"
            df.loc[index, "nombre"] = nombre
            logging.info(f"✅ Cuenta creada: {correo}")
        else:
            logging.warning(f"❌ Falló: {correo}")
        limpiar_cookies(driver)
        time.sleep(random.uniform(3, 6))
        procesados += 1
        if procesados >= CANTIDAD_CUENTAS:
            break
    guardar_excel(df, EXCEL_PATH)
    driver.quit()
    logging.info("Proceso finalizado.")

if __name__ == "__main__":
    main()
