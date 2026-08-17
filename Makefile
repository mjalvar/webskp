

.venv:
	python3 -m venv .venv

install:
	pip3 install -r requirements.txt


server: .venv
	uvicorn app:app --reload --port 8080