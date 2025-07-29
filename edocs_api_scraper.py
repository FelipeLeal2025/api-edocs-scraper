
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/edocs")
def consultar_edocs(q: str = Query(..., description="Número do processo")):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://e-docs.es.gov.br/processo/entrada")

    try:
        # Aguarda o campo de busca
        campo_busca = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "q"))
        )
        campo_busca.send_keys(q)

        # Clica no botão de lupa
        lupa = driver.find_element(By.ID, "onmi-lupa")
        lupa.click()

        # Aguarda o carregamento do conteúdo
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sob Custódia de:')]"))
        )

        # Encontra o texto
        elementos = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sob Custódia de:')]")
        if not elementos:
            return {"processo": q, "custodia": "Não encontrado"}

        texto = elementos[0].text
        custodia = texto.split("Sob Custódia de: ")[-1].strip()
        return {"processo": q, "custodia": custodia}

    except Exception as e:
        return {"erro": str(e)}
    finally:
        driver.quit()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
