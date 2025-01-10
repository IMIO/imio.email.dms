FROM python:3.10-buster

WORKDIR /tmp

RUN apt-get update \
    && apt-get install -y \
        dumb-init \
        locales \
        vim \
        xfonts-75dpi \
        xfonts-base \
    && wget -O wkhtmltox.deb "https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb" \
    && dpkg -i wkhtmltox.deb \
    && rm wkhtmltox.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/tmp/*

WORKDIR /app

COPY *.rst entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

COPY requirements.txt /app/requirements.txt
RUN ln -sf /usr/share/zoneinfo/Europe/Brussels /etc/localtime \
    && pip install -r requirements.txt

COPY buildout.cfg setup.py sources.cfg versions.cfg /app/
COPY src /app/src
RUN buildout

ENTRYPOINT ["/app/entrypoint.sh"]
