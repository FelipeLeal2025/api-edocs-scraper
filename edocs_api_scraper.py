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
def consultar_edocs(q: str = Query(..., description="Número do processo")):
    # Configurações do Chrome para execução headless
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        # Acessa a página de login do Acesso Cidadão
        driver.get("https://login.acessocidadao.es.gov.br/Entrar?urlRetorno=https%3A%2F%2Fe-docs.es.gov.br%2F")

        # Aguarda os campos carregarem e faz o login
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "CpfOuEmail"))).send_keys("03491959780")
        driver.find_element(By.ID, "Senha").send_keys("Le4l0317!")
        driver.find_element(By.ID, "btnEntrar").click()

        # Aguarda redirecionamento para o EDOCS
        WebDriverWait(driver, 20).until(EC.url_contains("e-docs.es.gov.br"))

        # Acessa diretamente a página de consulta de processos
        driver.get("https://e-docs.es.gov.br/processo/entrada")

        # Aguarda o campo de busca e realiza a consulta
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "q"))).send_keys(q)
        driver.find_element(By.ID, "onmi-lupa").click()

        # Aguarda carregamento dos dados
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "destaque-sob-custodia"))
        )

        # Extrai a custódia
        custodia_element = driver.find_element(By.CLASS_NAME, "destaque-sob-custodia")
        custodia_text = custodia_element.text.strip()
        return {"processo": q, "sob_custodia_de": custodia_text}

    except Exception as e:
        return {"erro": str(e)}

    finally:
        driver.quit()
