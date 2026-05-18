.PHONY: up down build test logs

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

test:
	pytest test_main.py -v -s

logs:
	docker-compose logs -f
