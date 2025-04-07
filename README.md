# League of Legends Tracker

## 📚 Explicación

**League of Legends Tracker** es una aplicación web diseñada para seguir estadísticas, campeones y otros aspectos del juego **League of Legends**. El objetivo de esta aplicación es proporcionar una forma sencilla y rápida para que los jugadores puedan consultar información actualizada sobre sus campeones favoritos, sus estadísticas, y mejorar su experiencia dentro del juego. Esta plataforma está diseñada tanto para jugadores casuales como para competidores serios que desean mejorar su rendimiento en el juego.

La aplicación está desarrollada utilizando **Django** en el backend y **Docker** para una configuración eficiente y escalable. Permite a los usuarios registrarse, iniciar sesión, consultar las estadísticas de los campeones y gestionar sus perfiles.

## 🛠️ Tecnologías Utilizadas

- **Django**: Framework web para backend.
- **Docker**: Contenedores para facilidad de desarrollo y despliegue.
- **Poetry**: Gestión de dependencias y empaquetado de Python.
- **HTML/CSS/JavaScript**: Para el frontend.

## 🚀 Instalación

Para comenzar a trabajar con **League of Legends Tracker**, sigue estos pasos:

### 1. Clona el repositorio

Primero, clona este repositorio en tu máquina local:

```bash
git clone https://github.com/tu_usuario/league-of-legends-tracker.git
cd league-of-legends-tracker
```

### 2. Configura el entorno de desarrollo

* **Usando Docker (Recomendado)**

Asegúrate de tener Docker y Docker Compose instalados en tu máquina.

Construye la imagen de Docker y levanta los contenedores:

```bash
docker-compose up --build
```

Accede a la aplicación a través de tu navegador en http://localhost:8000.

* **Sin Docker (Alternativa)**

Si prefieres no usar Docker, puedes configurar el entorno de desarrollo manualmente:

Instalar dependencias:

Asegúrate de tener Poetry instalado en tu máquina.

Instala las dependencias del proyecto:

```bash
poetry install
```

Aplicar migraciones de base de datos:

```bash
poetry run python manage.py migrate
```

Iniciar el servidor de desarrollo:

```bash
poetry run python manage.py runserver
```

Accede a la aplicación a través de tu navegador en http://localhost:8000.

## 👥 Integrantes del Equipo

* **Daniel Resa** - [Daniel](https://github.com/dresa04)
* **Arnau Solà** - [Arnau](https://github.com/Boira04)
* **Oriol Farràs** - [Oriol](https://github.com/Oriol-Farras)
* **Miquel Tomàs** - [Miquel](https://github.com/M4NU312)
* **Suhail Bendahan** - [Suhail](https://github.com/s890u)
