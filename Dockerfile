FROM python:3.7-buster

RUN apt-get update && apt-get install -y \
    dumb-init \
    locales \
    vim \
    xfonts-75dpi \
    xfonts-base

WORKDIR /tmp

RUN wget -O wkhtmltox.deb "https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb" && \
    dpkg -i wkhtmltox.deb && \
    rm wkhtmltox.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/tmp/*

ADD *.rst buildout.cfg entrypoint.sh requirements.txt setup.py sources.cfg versions.cfg /app/
ADD src /app/src

WORKDIR /app

RUN ln -sf /usr/share/zoneinfo/Europe/Brussels /etc/localtime

RUN chmod +x /app/entrypoint.sh

RUN pip install -r requirements.txt && \
    buildout

ENTRYPOINT ["/app/entrypoint.sh"]
