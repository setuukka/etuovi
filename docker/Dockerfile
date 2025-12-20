FROM python:3.12

RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN GECKO_VERSION=v0.33.0 \
    && wget -q https://github.com/mozilla/geckodriver/releases/download/$GECKO_VERSION/geckodriver-$GECKO_VERSION-linux64.tar.gz \
    && tar -xzf geckodriver-$GECKO_VERSION-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && rm geckodriver-$GECKO_VERSION-linux64.tar.gz


WORKDIR /app

COPY scripts/ /app/scripts
COPY docker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3"]

