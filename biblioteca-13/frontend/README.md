# Frontend — Biblioteca Serena (Vue 3)

Interfaz web moderna y minimalista en **Vue 3** (`<script setup>`, Composition API), **Pinia**, **Vue Router** y **Axios**, conectada a la API FastAPI de `biblioteca-13` y a las portadas almacenadas en **Cloudinary**.

## Requisitos previos

- Node.js 18+ y npm
- Backend FastAPI corriendo en `http://127.0.0.1:8000`

## Instalación y ejecución

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

La aplicación quedará disponible en `http://127.0.0.1:5173`. Vite usa ese mismo origen para enviar las peticiones `/api` al backend.

## Acceso y módulos

La ruta inicial solicita iniciar sesión. El registro público crea una cuenta de socio; al entrar, el sistema dirige al socio a su perfil y al personal al panel de gestión.

- **Administrador:** usuarios, libros, autores, categorías, socios, préstamos y reportes. Puede eliminar registros donde el backend lo autoriza.
- **Bibliotecario:** libros, autores, categorías, socios, préstamos y reportes, según los permisos de la API.
- **Socio:** catálogo, perfil, actualización de sus datos, cambio de contraseña, préstamos y multas propios.

La navegación y las acciones respetan los permisos existentes en FastAPI. Configura `VITE_API_URL` si la API no está disponible en `http://127.0.0.1:8000/api/v1`; si apuntas directamente a otro origen, habilita el origen del frontend en `CORS_ORIGINS`.
