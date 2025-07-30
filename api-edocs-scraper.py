from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

@app.route('/edocs', methods=['GET'])
def consulta_edocs():
    processo = request.args.get('q')
    if not processo:
        return jsonify({'erro': 'Parâmetro "q" (número do processo) é obrigatório'}), 400

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://e-docs.es.gov.br/")
        wait = WebDriverWait(driver, 10)

        # Localizar campo de busca pelo id="q"
        campo_busca = wait.until(EC.presence_of_element_located((By.ID, "q")))
        campo_busca.send_keys(processo)
        campo_busca.send_keys(Keys.ENTER)

        # Aguardar redirecionamento e carregamento
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sob Custódia de:')]")))

        # Encontrar o bloco que contém o texto "Sob Custódia de:"
        elemento_custodia = driver.find_element(By.XPATH, "//*[contains(text(), 'Sob Custódia de:')]/following-sibling::div")
        texto_custodia = elemento_custodia.text.strip()

        return jsonify({'processo': processo, 'sob_custodia': texto_custodia})

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
