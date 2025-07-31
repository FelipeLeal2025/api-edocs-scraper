from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
def get_custody_info(q: str = Query(..., description="Número do processo")):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.get("https://e-docs.es.gov.br")

    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "q"))
        )
        search_input.send_keys(q)
        search_input.submit()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sob Custódia de:')]"))
        )

        element = driver.find_element(By.XPATH, "//*[contains(text(), 'Sob Custódia de:')]/following-sibling::*")
        result = element.text
    except Exception as e:
        result = f"Erro ao buscar custódia: {e}"
    finally:
        driver.quit()

    return {"custodia": result}
