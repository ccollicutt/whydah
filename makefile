.PHONY: build run refresh

build:
	pip install -r requirements.txt

run:
	FLASK_APP=whydah.app:create_app FLASK_ENVIRONMENT=development FLASK_RUN_PORT=5100 flask run

refresh:
	curl -X POST http://localhost:5100/config/refresh

get-service:
	curl http://localhost:5100/config/service1
	curl http://localhost:5100/config/superservice

update-service:
	curl -X POST -H "Content-Type: application/json" -d '{"value": "newstring"}' http://localhost:5100/config/service1/feature1

test:
	cd whydah/tests && pytest -v

reload-direnv:
	direnv allow && direnv reload

loc:
	cd whydah && find . -name '*.py' | xargs wc -l

build-image:
	docker build -t whydah:latest .

run-image:
	docker rm whydah || true
	docker run --name whydah \
	-e GIT_REPO_URL="https://github.com/ccollicutt/python-service-config-examples/" \
	-p 8000:8000 whydah:latest
