python -m venv .\.venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Start-Process python testMiur.py
start chrome.exe "http://127.0.0.1:5000"
