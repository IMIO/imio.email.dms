#!/usr/bin/make

image_name=imio.email.dms
config_file=config.ini
counters_directory=/tmp/counters
pdf-output-dir=/tmp/pdf

process:
	docker run -it --rm -v $(config_file):/config.ini -v $(counters_directory):/tmp/counters --tmpfs $(pdf-output-dir) $(image_name) /config.ini

build-docker:
	docker build -t $(image_name) .
