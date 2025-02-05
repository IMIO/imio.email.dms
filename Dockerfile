FROM harbor.imio.be/common/base:py3-ubuntu-22.04 AS builder

RUN apt-get update \
    && apt-get install -y \
        gcc \
        git \
        libjpeg62-dev \
        libxml2-dev \
        libxslt1-dev \
        python3-dev

WORKDIR /home/imio/

COPY --chown=imio requirements.txt /home/imio/requirements.txt
RUN pip install -r requirements.txt

COPY --chown=imio src /home/imio/src
COPY --chown=imio *.cfg *.rst setup.py /home/imio/
RUN su -c "buildout -c buildout.cfg -t 30 -N" -s /bin/sh imio


FROM harbor.imio.be/common/base:py3-ubuntu-22.04

ADD https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb /tmp/wkhtmltox.deb

RUN apt-get update \
    && apt-get install -y \
        dumb-init \
        fontconfig \
        ghostscript \
        libjpeg-turbo8 \
        libjpeg62-dev \
        libmagic-dev \
        libmagic1 \
        libopenjp2-7-dev \
        libxext6 \
        libxrender1 \
        xfonts-75dpi \
        xfonts-base \
    && dpkg -i /tmp/wkhtmltox.deb \
    && rm /tmp/wkhtmltox.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/tmp/*

WORKDIR /home/imio/

COPY --from=builder --chown=imio /home/imio .
COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
COPY --chown=imio --chmod=500 entrypoint.sh /home/imio/entrypoint.sh

# USER imio

ENTRYPOINT ["/home/imio/entrypoint.sh"]
