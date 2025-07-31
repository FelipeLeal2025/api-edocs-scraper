from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/edocs")
def consulta_edocs(q: str = Query(..., description="Número do processo EDOCS")):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://login.acessocidadao.es.gov.br/Entrar?urlRetorno=https%3A%2F%2Facessocidadao.es.gov.br%2Fconta%2FGetParaLoginNovo")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Login")))
        driver.find_element(By.NAME, "Login").send_keys(os.environ["EDOCS_USER"])
        driver.find_element(By.NAME, "Senha").send_keys(os.environ["EDOCS_PASS"])
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ACESSAR')]")))
        driver.find_element(By.XPATH, "//button[contains(., 'ACESSAR')]").click()

        WebDriverWait(driver, 10).until(EC.url_contains("e-docs.es.gov.br/Internal"))

        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "q")))
        search_box.clear()
        search_box.send_keys(q)
        search_box.submit()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Sob Custódia de:')]")))
        label = driver.find_element(By.XPATH, "//*[contains(text(),'Sob Custódia de:')]")
        result = label.find_element(By.XPATH, "./following-sibling::*").text.strip()

        return {"custodia": result}

    except Exception as e:
        return {"erro": str(e)}

    finally:
        driver.quit()
