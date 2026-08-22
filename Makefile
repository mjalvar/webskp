
# skp a fbx
# https://anyconv.com/skp-converter/

.venv:
	python3 -m venv .venv

install:
	pip3 install -r requirements.txt

server: .venv
	uvicorn app:app --reload --port 8080

deploy:
	@APP_VERSION="dev-$$(date -u +%Y%m%d-%H%M%S)"; \
	echo "Deploying APP_VERSION=$$APP_VERSION"; \
	fly deploy --build-arg APP_VERSION="$$APP_VERSION"