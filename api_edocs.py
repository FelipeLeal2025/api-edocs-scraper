from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

@app.route('/edocs', methods=['GET'])
def get_edocs_data():
    processo = request.args.get('q')
    if not processo:
        return jsonify({"error": "Parâmetro 'q' é obrigatório"}), 400

    url = f"https://e-docs.es.gov.br/Processo/Protocolo/{processo}"

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(url)

        # Aguarda elemento com texto 'Sob Custódia de:' aparecer
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sob Custódia de:')]"))
        )
        time.sleep(1)

        # Extrai o conteúdo logo após "Sob Custódia de:"
        custodia_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Sob Custódia de:')]/following-sibling::div[1]")
        custodia_text = custodia_element.text.strip()

        return jsonify({
            "processo": processo,
            "custodia": custodia_text
        })
    except (NoSuchElementException, TimeoutException):
        return jsonify({
            "processo": processo,
            "custodia": "Não localizado"
        }), 404
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
