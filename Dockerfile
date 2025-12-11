FROM mongo:7.0

# 1. Ставим системные зависимости и Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Ставим Poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION="1.8.3" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s ${POETRY_HOME}/bin/poetry /usr/local/bin/poetry

# 3. Копируем только pyproject/lock для кеширования слоёв
WORKDIR /app
COPY pyproject.toml ./
# если есть: COPY poetry.lock ./

# 4. Устанавливаем зависимости (создаст .venv в /app)
RUN poetry install --no-root --only main

# 5. Копируем остальной исходный код
COPY . .

EXPOSE 27017

# Запуск только MongoDB, без сидера
CMD ["mongod", "--bind_ip_all"]
