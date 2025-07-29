from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import uvicorn
import time

app = FastAPI()

@app.get("/edocs")
def get_custodia(q: str = Query(..., description="Número do processo EDOCS ex: 2025-KL88R")):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        url = f"https://e-docs.es.gov.br/Processo/Protocolo/{q}"
        driver.get(url)
        time.sleep(5)

        custodia_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Sob Custódia de:')]/following-sibling::*")
        custodia = custodia_element.text.strip()

        driver.quit()

        return JSONResponse(content={"processo": q, "custodia": custodia})

    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        return JSONResponse(content={"erro": str(e)}, status_code=500)
