API de Scraping do EDOCS (ES)

▶️ Como usar:

1. Instale os pacotes:
   pip install -r requirements.txt

2. Baixe o ChromeDriver compatível com sua versão do Chrome:
   https://chromedriver.chromium.org/downloads

   → Coloque o chromedriver no mesmo diretório do script ou no PATH do sistema.

3. Inicie a API:
   uvicorn api_edocs:app --host 0.0.0.0 --port 8000

4. Acesse no navegador:
   http://localhost:8000/edocs?q=2025-KL88R

Retorno JSON com a informação de "Sob Custódia de".
