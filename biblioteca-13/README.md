# Taller 2 – API REST segura con FastAPI: autenticación, autorización y migraciones (Biblioteca)

API REST de nivel de producción para la gestión de una biblioteca, construida con **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, **PostgreSQL**, **PyJWT (HS256)**, **Argon2 (`pwdlib`)** y **SlowAPI**.

---

## Requisitos

- Python 3.12+
- PostgreSQL 15+ (local o mediante Docker)

---

## 1. Instalación

1. Clonar el repositorio y entrar a la carpeta del proyecto:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements-dev.txt
   ```
2. Levantar la base de datos con Docker Compose (opcional si ya tienes PostgreSQL local):
   ```powershell
   docker compose up -d db
   ```
3. Copiar `.env.example` a `.env` y configurar las variables de entorno.

---

## 2. Variables de entorno (`.env`)

Genera una clave segura de al menos 32 caracteres:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

| Variable | Ejemplo | Uso |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://postgres:1234@localhost:5432/biblioteca` | Conexión principal de la API |
| `TEST_DATABASE_URL` | `postgresql+psycopg://postgres:1234@localhost:5432/biblioteca_test` | Base de datos exclusiva para `pytest` |
| `SECRET_KEY` | *(mínimo 32 caracteres)* | Firma de los JSON Web Tokens |
| `ALGORITHM` | `HS256` | Algoritmo de firma JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Duración del access token en minutos |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Duración del refresh token en días |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Orígenes frontend permitidos por CORS |
| `ENVIRONMENT` | `dev` \| `test` \| `prod` | Entorno de ejecución (`prod` oculta `/docs` y `/redoc`) |

---

## 3. Migraciones con Alembic

La base de datos se gestiona exclusivamente mediante migraciones versionadas de Alembic:

```powershell
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Ver versión actual e historial
alembic current
alembic history

# Revertir todas las migraciones y volver a aplicarlas
alembic downgrade base
alembic upgrade head
```

### Historial de migraciones incluidas
| Migración | Fase | Descripción |
| --- | --- | --- |
| `0001_estado_inicial` | 2 | Tablas iniciales: `autores`, `categorias`, `libros`, `libro_categoria`, `socios`, `prestamos` |
| `0002_multa_pagada` | 2 | Columna `prestamos.multa_pagada` + migración de datos |
| `0003_usuarios` | 3 | Tabla `usuarios`, enum `rolusuario` y relación 1 a 1 con `socios` |
| `0004_refresh_tokens` | 4 | Tabla `refresh_tokens` para rotación y revocación de tokens |
| `0005_auditoria_prestamos` | 5 | Columna `prestamos.registrado_por_id` (FK a `usuarios.id`) |

---

## 4. Creación del primer administrador

Nadie puede registrarse como administrador desde la API pública. Para crear el primer usuario con rol `admin`, ejecuta el script interactivo:

```powershell
python -m app.scripts.crear_admin
```

---

## 5. Ejecución de la API

```powershell
fastapi dev app/main.py
# o con uvicorn:
uvicorn app.main:app --reload
```

- Documentación interactiva (Swagger UI): `http://127.0.0.1:8000/docs`
- Verificación de salud: `GET http://127.0.0.1:8000/api/v1/health`

---

## 6. Pruebas automatizadas y cobertura

```powershell
pytest --cov=app
```

---

## 6.1. Despliegue

El proyecto incluye todo lo necesario para publicarlo sin cambios adicionales: el
`Dockerfile` aplica las migraciones (`alembic upgrade head`) y luego arranca
uvicorn en el puerto que indique la plataforma (`$PORT`).

### Docker local

```powershell
docker compose up -d --build
# API: http://127.0.0.1:8000/docs  |  Salud: http://127.0.0.1:8000/api/v1/health
```

### Render (recomendado, plan gratuito)

1. Sube el proyecto a GitHub.
2. En Render: **New → Blueprint** y selecciona el repositorio; se leerá `render.yaml`,
   que crea la base de datos PostgreSQL y el servicio web automáticamente.
3. Render genera `SECRET_KEY` y `DATABASE_URL` por ti. Ajusta `CORS_ORIGINS` al
   dominio real del frontend (variable de entorno del servicio `biblioteca-api`).
4. Crea el primer administrador desde la consola del servicio:
   ```bash
   python -m app.scripts.crear_admin
   ```

> La URL de conexión que entrega Render (`postgresql://...`) se convierte
> automáticamente al driver `psycopg` 3, no hace falta editarla.

### Fly.io

```bash
fly launch --no-deploy     # usa el fly.toml incluido
fly postgres create
fly postgres attach <nombre-de-la-bd>   # define DATABASE_URL
fly secrets set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
fly deploy
```

```bash
fly status
fly logs
```

### Variables obligatorias en producción

| Variable | Valor |
| --- | --- |
| `DATABASE_URL` | Cadena de conexión de la plataforma |
| `SECRET_KEY` | Mínimo 32 caracteres, generada aleatoriamente |
| `ENVIRONMENT` | `prod` (oculta `/docs` y `/redoc`, exige CORS explícito) |
| `CORS_ORIGINS` | Lista JSON con el dominio del frontend, sin `*` |

---

## 7. Roles del sistema

| Rol | Quién es | Qué puede hacer |
| --- | --- | --- |
| **anónimo** | Usuario sin token | Registrarse, iniciar sesión, renovar token y consultar el catálogo |
| **socio** | Persona inscrita vinculada a un registro en `socios` | Ver y editar su propio perfil (`/socios/me`), consultar sus préstamos y sus multas |
| **bibliotecario** | Empleado de la biblioteca | Gestionar catálogo (crear/editar), gestionar socios, registrar préstamos, devoluciones y pagos de multas, consultar reportes |
| **admin** | Administrador del sistema | Todo lo anterior, eliminar recursos del catálogo/socios y gestionar usuarios y roles (`/usuarios`) |

---

## 8. Tabla de endpoints y matriz de permisos

Todos los endpoints están bajo el prefijo `/api/v1`:

| Endpoint | Anónimo | Socio | Bibliotecario | Admin |
| --- | :---: | :---: | :---: | :---: |
| `POST /auth/registro`, `/auth/login`, `/auth/refresh`, `GET /health` | Sí | Sí | Sí | Sí |
| `GET /libros`, `/autores`, `/categorias` | Sí | Sí | Sí | Sí |
| `POST / PATCH /libros`, `/autores`, `/categorias` | No | No | Sí | Sí |
| `DELETE /libros`, `/autores`, `/categorias` | No | No | No | Sí |
| `GET /auth/me`, `POST /auth/logout`, `PATCH /auth/me/password` | No | Sí | Sí | Sí |
| `GET /socios`, `POST /socios` | No | No | Sí | Sí |
| `GET /socios/me`, `PATCH /socios/me`, `GET /socios/me/prestamos`, `GET /socios/me/multas` | No | Propio | No | No |
| `GET /socios/{id}`, `PATCH /socios/{id}`, `GET /socios/{id}/prestamos` | No | No | Sí | Sí |
| `DELETE /socios/{id}` | No | No | No | Sí |
| `GET /prestamos`, `GET /prestamos/{id}` | No | Propio | Sí | Sí |
| `POST /prestamos`, `POST /prestamos/{id}/devolucion`, `POST /prestamos/{id}/pago-multa` | No | No | Sí | Sí |
| `GET /reportes/*` | No | No | Sí | Sí |
| `GET /usuarios`, `POST /usuarios`, `PATCH /usuarios/{id}/rol`, `PATCH /usuarios/{id}/activo` | No | No | No | Sí |

---

