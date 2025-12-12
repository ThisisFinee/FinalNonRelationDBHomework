FROM mongo:7.0

RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

WORKDIR /app
COPY pyproject.toml ./
COPY poetry.lock ./

RUN poetry install --no-root --only main

COPY . .

EXPOSE 27017

CMD ["mongod", "--bind_ip_all"]
