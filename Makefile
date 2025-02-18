#!/usr/bin/make
all: buildout

IMAGE_NAME="iadocs/dms/mail:latest"

.PHONY: setup
setup:  ## Setups environment
	virtualenv .
	./bin/pip install --upgrade pip
	./bin/pip install -r requirements.txt

.PHONY: buildout
buildout:  ## Runs setup and buildout
	if ! test -f bin/buildout;then make setup;fi
	./bin/buildout -v

docker-image:
	mkdir -p eggs
	docker build --no-cache --pull -t $(IMAGE_NAME) .

lint:
	pre-commit run --all

.PHONY: vcr
vcr:  ## Shows requirements in checkversion-r.html
	bin/versioncheck -rbo checkversion-r.html

.PHONY: vcn
vcn:  ## Shows newer packages in checkversion-n.html
	bin/versioncheck -npbo checkversion-n.html

.PHONY: cleanall
cleanall:  ## Cleans all installed buildout files
	rm -fr bin include lib local share develop-eggs downloads eggs parts .installed.cfg .plone.versioncheck.tracked.json .mr.developer.cfg
