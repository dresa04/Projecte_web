FROM python:3.13-slim

# Defineix la carpeta de treball dins del contenidor
WORKDIR /app

# Instal·la Poetry
RUN pip install poetry

# Copia només els fitxers de dependències primer (per cache eficient)
COPY pyproject.toml poetry.lock ./

# Desactiva entorns virtuals i instal·la les dependències sense instal·lar el projecte mateix
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Ara copia la resta del projecte
COPY . .

# Exposa el port on s'executa Django
EXPOSE 8000

# Comanda per arrencar el servidor de desenvolupament de Django
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
