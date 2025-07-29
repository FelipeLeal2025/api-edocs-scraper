
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

        # Aguarda o carregamento do conteúdo com a classe desejada
        elemento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//span[contains(text(), ' - ') and contains(@class, 'mdc-typography--body2')]"
            ))
        )

        custodia = elemento.text.strip()
        return {"processo": q, "custodia": custodia}

    except Exception as e:
        return {"erro": str(e)}
    finally:
        driver.quit()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
