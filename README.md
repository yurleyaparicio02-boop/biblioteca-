# API REST de biblioteca

API de gestión bibliotecaria desarrollada con FastAPI, SQLAlchemy y PostgreSQL.
La aplicación organiza las responsabilidades en routers, controladores, esquemas,
modelos y servicios centrales.

## Requisitos

- Python 3.10 o posterior
- PostgreSQL en ejecución y una base de datos vacía creada

## Instalación y ejecución

Desde la raíz del proyecto, crea y activa un entorno virtual e instala las
dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copia `.env.example` como `.env` y asigna la URL de tu base de datos:

```dotenv
DATABASE_URL=postgresql+psycopg://usuario:contrasena@localhost:5432/biblioteca
```

No publiques `.env`: contiene credenciales. Al iniciar, la aplicación crea las
tablas que todavía no existan. `create_all` **no** modifica tablas existentes:
si vienes de una versión anterior del proyecto, usa una base nueva y vacía.

```powershell
uvicorn app.main:app --reload
```

La documentación interactiva queda disponible en
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Endpoints

| Recurso | Operaciones |
| --- | --- |
| Autores | `GET/POST /autores`, `GET/PATCH/DELETE /autores/{autor_id}`, `GET /autores/{autor_id}/libros` |
| Categorías | `GET/POST /categorias`, `GET/PATCH/DELETE /categorias/{categoria_id}` |
| Libros | `GET/POST /libros`, `GET/PATCH/DELETE /libros/{libro_id}` |
| Socios | `GET/POST /socios`, `GET/PATCH/DELETE /socios/{socio_id}`, `GET /socios/{socio_id}/prestamos` |
| Préstamos | `GET/POST /prestamos`, `GET /prestamos/{prestamo_id}`, `POST /prestamos/{prestamo_id}/devolucion`, `POST /prestamos/{prestamo_id}/multa/pago` |
| Reportes | `GET /reportes/libros-mas-prestados`, `/categorias`, `/prestamos-vencidos`, `/socios-con-multas`, `/autores` y `/resumen` |

### Respuesta paginada

Todos los listados aceptan `skip` (desde 0) y `limit` (entre 1 y 100) y
devuelven un sobre con la metadata de la página:

```json
{
  "items": [ ... ],
  "total": 42,
  "skip": 0,
  "limit": 20,
  "paginas": 3
}
```

`total` es el número de registros que cumplen los filtros (no el de la página)
y `paginas` el total de páginas para ese `limit`.

Los endpoints de libros aceptan filtros `buscar`, `autor`, `categoria_id`,
`desde`, `hasta` y `orden`; los préstamos aceptan filtros por estado, socio y
libro. Los textos de búsqueda se comparan de forma literal: `%` y `_` se buscan
como caracteres, no como comodines.

## Reglas de negocio

- Un socio activo puede tener como máximo 3 préstamos abiertos.
- No se presta si el socio tiene préstamos vencidos, ya tiene ese libro o
  **tiene multas pendientes de pago**.
- No se presta un libro sin ejemplares disponibles (con bloqueo de fila para
evitar carreras entre peticiones simultáneas).
- `fecha_prestamo` no puede ser futura ni tan antigua que el préstamo nazca
vencido.
- `fecha_devolucion` no puede ser anterior al préstamo ni futura.

### Multas

- Se cobran **0.50 por cada día** de retraso sobre `fecha_limite`, calculadas en
  el momento de registrar la devolución.
- Cada préstamo expone `multa`, `multa_pagada` y `estado_multa`
  (`sin_multa`, `pendiente` o `pagada`).
- Mientras un socio tenga **alguna multa pendiente no puede tomar préstamos**.
- `POST /prestamos/{prestamo_id}/multa/pago` marca la multa como pagada
  (409 si ya estaba pagada, 422 si el préstamo sigue abierto o no tiene multa).
- `GET /reportes/socios-con-multas?solo_pendientes=true` lista las deudas; con
  `false` incluye también las saldadas. `GET /reportes/resumen` añade
  `multas_pendientes` además de `total_multas`.

```powershell
# Ejemplo: cobrar una multa
curl -X POST http://127.0.0.1:8000/prestamos/12/multa/pago
```

## Estructura

```text
app/
├── controllers/
├── core/
├── models/
├── routes/
├── schemas/
└── main.py
```

## Integrantes

Completa aquí los nombres de los integrantes antes de entregar.
