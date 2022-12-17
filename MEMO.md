python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

./Pali_searcher.py
STATIC_URL=https://www.example.com/static/ ./Pali_searcher.py

deactivate

python3 -m venv .venv
source .venv/bin/activate

pip install flask

pip freeze > requirements.txt

