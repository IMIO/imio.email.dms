#!/usr/bin/make
all: buildout

IMAGE_NAME="iadocs/dms/mail:latest"

docker-image:
	mkdir -p eggs
	docker build --pull -t $(IMAGE_NAME) .

lint:
	pre-commit run --all
