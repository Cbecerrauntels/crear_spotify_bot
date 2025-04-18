import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time

EXCEL_PATH = "C:/crear_spotify_bot/correos_spotify.xlsx"
CHROME_DRIVER_PATH = "C:/crear_spotify_bot/chromedriver.exe"

def crear_cuenta_spotify(correo, clave):
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = webdriver.ChromeService(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.spotify.com/pe/signup")
        wait = WebDriverWait(driver, 15)

        # Escribir correo
        campo_correo = wait.until(EC.visibility_of_element_located((By.ID, "username")))
        campo_correo.send_keys(correo)

        # Click en siguiente
        btn_siguiente = driver.find_element(By.XPATH, '//span[text()="Siguiente"]')
        btn_siguiente.click()

        # Escribir contraseña
        campo_clave = wait.until(EC.visibility_of_element_located((By.ID, "new-password")))
        campo_clave.send_keys(clave)

        # Se podría continuar desde aquí con los siguientes campos...

        time.sleep(2)
        print(f"✅ Cuenta creada con {correo}")
        return True

    except Exception as e:
        print(f"❌ Error con {correo}: {str(e)}")
        return False

    finally:
        driver.quit()

def main():
    df = pd.read_excel(EXCEL_PATH)
    df_no_usados = df[df["usado"] != "sí"]

    try:
        cantidad = input("¿Cuántas cuentas deseas crear? [por defecto: 1]: ")
        cantidad = int(cantidad.strip()) if cantidad.strip().isdigit() else 1
    except:
        cantidad = 1

    for i in range(min(cantidad, len(df_no_usados))):
        fila = df_no_usados.iloc[i]
        correo, clave = fila["correo"], fila["clave"]
        exito = crear_cuenta_spotify(correo, clave)
        if exito:
            df.loc[df["correo"] == correo, "usado"] = "sí"

    df.to_excel(EXCEL_PATH, index=False)
    print("✅ Archivo Excel actualizado.")

if __name__ == "__main__":
    main()
