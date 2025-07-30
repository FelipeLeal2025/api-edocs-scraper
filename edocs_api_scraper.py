from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

app = Flask(__name__)

@app.route("/edocs", methods=["GET"])
def edocs_scraper():
    processo = request.args.get("q")
    if not processo:
        return jsonify({"error": "Parâmetro 'q' (número do processo) é obrigatório."}), 400

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    url = "https://e-docs.es.gov.br/"
    driver.get(url)

    try:
        # Aguarda campo de busca
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "q"))
        )
        search_input.send_keys(processo)
        search_input.submit()

        # Aguarda a navegação
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sob Custódia de:')]"))
        )
        time.sleep(2)  # garante que DOM está estável

        # Extrai a custódia
        custodia_element = driver.find_element(By.CLASS_NAME, "destaque-sob-custodia")
        custodia = custodia_element.text.strip()

    except (TimeoutException, NoSuchElementException) as e:
        driver.quit()
        return jsonify({"error": "Informação de custódia não encontrada.", "detalhe": str(e)}), 404

    driver.quit()
    return jsonify({"custodia": custodia})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
