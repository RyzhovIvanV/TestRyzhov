```
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # macOS / Linux
pip install -r requirements.txt
playwright install chromium

pytest                    
pytest -m auth         
pytest -m e2e                   
allure serve allure-results     
HEADLESS=false SLOW_MO_MS=500 pytest -s
```

