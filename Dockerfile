FROM wkhtmltox

ADD *.rst buildout.cfg requirements.txt setup.py sources.cfg versions.cfg /app/
ADD src /app/src

WORKDIR /app

RUN pip install -r requirements.txt && \
    buildout

ENTRYPOINT ["/app/bin/process_mails"]
