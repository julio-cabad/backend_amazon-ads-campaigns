# 🚀 Backend Amazon Ads Campaigns

Backend de nivel empresarial para la gestión de campañas de Amazon Ads, construido con **Django**, **DRF** y **Domain-Driven Design (DDD)**. Simula integraciones con la API externa de Amazon Ads utilizando tareas asíncronas y patrones resilientes.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0-green.svg)
![Celery](https://img.shields.io/badge/Celery-5.4-orange.svg)
![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)

---

## 🏗 Arquitectura

El proyecto sigue una arquitectura **Domain-Driven Design (DDD)** estructurada para escalar:

```
backend/
├── apps/
│   └── campaigns/          # Dominio principal
│       ├── api/            # Capa de presentación (Views, Serializers)
│       ├── domain/         # Lógica de negocio pura (Models, Services)
│       └── tasks/          # Tareas asíncronas (Celery)
├── integrations/
│   └── amazon_ads/         # Cliente simulado de Amazon Ads (con AWS4Auth)
└── config/                 # Configuración por entornos
```

### ✨ Características Principales

1.  **Gestión de Campañas**: CRUD completo con estados (`PENDING`, `PROCESSING`, `ACTIVE`, `FAILED`).
2.  **Integración Asíncrona**: Uso de **Celery** para crear campañas en Amazon en segundo plano sin bloquear al usuario.
3.  **Sincronización Automática**: **Celery Beat** actualiza el estado de las campañas cada minuto.
4.  **Resiliencia**: Implementación de **Retry Logic** con backoff exponencial para fallos de red o rate limits.
5.  **Simulación Realista**: Cliente Amazon Ads que simula latencia, errores (20%) y transiciones de estado.
6.  **Calidad de Código**: Tipado estático, logging estructurado (`structlog`) y validaciones robustas.

---

## 🛠 Requisitos Previos

- Python 3.11+
- Redis (para Celery)
- Docker (opcional, para levantar todo el stack)

---

## 🌐 Demo en Vivo

El backend está desplegado y funcionando en Railway:

*   **API Base**: [https://backendamazon-ads-campaigns-production.up.railway.app/](https://backendamazon-ads-campaigns-production.up.railway.app/)
*   **Documentación Swagger**: [https://backendamazon-ads-campaigns-production.up.railway.app/api/docs/](https://backendamazon-ads-campaigns-production.up.railway.app/api/docs/)
*   **Health Check**: [https://backendamazon-ads-campaigns-production.up.railway.app/api/health/](https://backendamazon-ads-campaigns-production.up.railway.app/api/health/)

---

## 🚀 Guía de Inicio Rápido

### 1. Clonar y Configurar

```bash
# Clonar repositorio
git clone <tu-repo>
cd backend_amazon-ads-campaigns

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements/development.txt

# Configurar variables de entorno
cp .env.example .env
```

### 2. Base de Datos y Migraciones

El proyecto usa **SQLite** por defecto para facilitar la prueba, pero soporta **PostgreSQL** cambiando la variable `DATABASE_URL`.

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### 3. Ejecutar Servicios

Necesitarás 3 terminales (o usar Docker):

**Terminal 1: Servidor Django**
```bash
python manage.py runserver
```

**Terminal 2: Worker de Celery** (Procesa tareas en background)
```bash
# Asegúrate de tener Redis corriendo (redis-server)
celery -A config worker -l info
```

**Terminal 3: Celery Beat** (Planificador de tareas periódicas)
```bash
celery -A config beat -l info
```

---

## 🧪 Pruebas y Desarrollo

### Ejecutar Tests
Usamos `pytest` para una experiencia de testing moderna y rápida.

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con reporte de cobertura
pytest --cov=apps

# Ejecutar tests específicos
pytest tests/unit/campaigns/test_services.py
```

### Documentación API (Swagger)
Una vez corriendo el servidor, visita:
- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)

---

## 📦 Docker (Opción recomendada)

Si tienes Docker instalado, puedes levantar todo el entorno con un solo comando:

```bash
docker-compose up --build
```

Esto levantará:
- Backend Django (Puerto 8000)
- PostgreSQL
- Redis
- Celery Worker
- Celery Beat

---

## ☁️ Despliegue en Producción (Railway)

Este proyecto está optimizado para desplegarse fácilmente en [Railway](https://railway.app/).

1.  **Fork/Clone** este repositorio.
2.  Crea un nuevo proyecto en Railway desde GitHub.
3.  Añade una base de datos **PostgreSQL** y un servicio **Redis** desde el panel de Railway.
4.  Configura las siguientes **Variables de Entorno** en tu servicio Backend:
    *   `DATABASE_URL`: (La URL de conexión de Postgres)
    *   `REDIS_URL`: (La URL de conexión de Redis)
    *   `DJANGO_SETTINGS_MODULE`: `config.settings.production`
    *   `SECRET_KEY`: (Crea una clave segura)
    *   `ALLOWED_HOSTS`: `*` (o tu dominio real)
5.  Railway detectará automáticamente el `Dockerfile` en la raíz y desplegará el servicio.

---

## 📝 Decisiones Técnicas

1.  **SQLite vs PostgreSQL**: Se configuró SQLite por defecto para cumplir con la facilidad de ejecución de la prueba técnica, pero la arquitectura está lista para producción con PostgreSQL.
2.  **UUIDs**: Se usaron UUIDs para IDs de campaña para evitar enumeración y colisiones en sistemas distribuidos.
3.  **Structlog**: Logging en formato JSON para facilitar la ingestión en sistemas como ELK o Datadog.
4.  **Tenacity**: Librería para manejo robusto de reintentos en el cliente HTTP.

---
**Desarrollado con ❤️ para la Prueba Técnica Full Stack Amazon Ads**
