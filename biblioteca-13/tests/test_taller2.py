from datetime import date, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hashear_password, limiter
from app.models.usuario import RolUsuario, Usuario
from app.scripts.crear_admin import crear_administrador


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _login(client: TestClient, email: str, password: str):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )


def test_flujo_completo_33_casos_y_cobertura(
    client: TestClient, db_session: Session
):
    """Ejecuta en orden los datos iniciales y los 31 casos funcionales de la guía."""
    # Caso 31: GET /api/v1/health -> 200 { "status": "ok", "database": "ok" }
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    assert res_health.json() == {"status": "ok", "database": "ok"}
    assert "X-Request-ID" in res_health.headers

    # Paso previo 1: Crear el admin: admin@biblioteca.com
    admin = db_session.scalar(
        select(Usuario).where(Usuario.email == "admin@biblioteca.com")
    )
    if not admin:
        admin = Usuario(
            email="admin@biblioteca.com",
            nombre="Admin Biblioteca",
            password_hash=hashear_password("Admin1234"),
            rol=RolUsuario.admin,
            activo=True,
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)

    res_login_admin = _login(client, "admin@biblioteca.com", "Admin1234")
    assert res_login_admin.status_code == 200
    admin_token = res_login_admin.json()["access_token"]

    # Paso previo 2: Con el token del admin crear el bibliotecario: biblio@biblioteca.com
    res_crear_biblio = client.post(
        "/api/v1/usuarios",
        headers=_auth_header(admin_token),
        json={
            "email": "biblio@biblioteca.com",
            "nombre": "Biblio Empleado",
            "password": "Biblio1234",
            "rol": "bibliotecario",
        },
    )
    assert res_crear_biblio.status_code == 201
    biblio_id = res_crear_biblio.json()["id"]

    res_login_biblio = _login(client, "biblio@biblioteca.com", "Biblio1234")
    assert res_login_biblio.status_code == 200
    biblio_token = res_login_biblio.json()["access_token"]

    # Caso 1: Registro con password "abcdefgh" -> 422 (sin mayúscula ni número)
    res_c1 = client.post(
        "/api/v1/auth/registro",
        json={
            "email": "invalido1@example.com",
            "nombre": "Usuario Invalido",
            "password": "abcdefgh",
            "confirmar_password": "abcdefgh",
        },
    )
    assert res_c1.status_code == 422

    # Caso 2: Registro con password y confirmar_password distintos -> 422
    res_c2 = client.post(
        "/api/v1/auth/registro",
        json={
            "email": "invalido2@example.com",
            "nombre": "Usuario Invalido",
            "password": "Password123",
            "confirmar_password": "Password999",
        },
    )
    assert res_c2.status_code == 422

    # Caso 3: Registro válido de Ana -> 201, rol socio, socio_id con valor y sin password_hash
    res_c3 = client.post(
        "/api/v1/auth/registro",
        json={
            "email": "ana@example.com",
            "nombre": "ana torres",
            "telefono": "3001112233",
            "password": "AnaPassword1",
            "confirmar_password": "AnaPassword1",
        },
    )
    assert res_c3.status_code == 201
    ana_data = res_c3.json()
    assert ana_data["rol"] == "socio"
    assert ana_data["socio_id"] is not None
    assert "password_hash" not in ana_data
    assert "password" not in ana_data
    ana_socio_id = ana_data["socio_id"]

    # Registrar también a Luis Pérez (luis@example.com)
    res_luis = client.post(
        "/api/v1/auth/registro",
        json={
            "email": "luis@example.com",
            "nombre": "Luis Perez",
            "telefono": "3002223344",
            "password": "LuisPassword1",
            "confirmar_password": "LuisPassword1",
        },
    )
    assert res_luis.status_code == 201
    luis_data = res_luis.json()
    luis_user_id = luis_data["id"]
    luis_socio_id = luis_data["socio_id"]

    # Caso 4: Registro de Ana otra vez con "ANA@EXAMPLE.COM" -> 409
    res_c4 = client.post(
        "/api/v1/auth/registro",
        json={
            "email": "ANA@EXAMPLE.COM",
            "nombre": "Ana Torres",
            "password": "AnaPassword1",
            "confirmar_password": "AnaPassword1",
        },
    )
    assert res_c4.status_code == 409

    # Caso 5: Login de Ana con contraseña incorrecta -> 401 "Credenciales inválidas"
    res_c5 = _login(client, "ana@example.com", "ClaveErronea1")
    assert res_c5.status_code == 401
    assert res_c5.json()["detail"] == "Credenciales inválidas"

    # Caso 6: Login con un email que no existe -> 401 con el mismo mensaje del caso 5
    res_c6 = _login(client, "noexiste@example.com", "ClaveErronea1")
    assert res_c6.status_code == 401
    assert res_c6.json()["detail"] == res_c5.json()["detail"]

    # Caso 7: Login correcto de Ana -> 200 con access_token, refresh_token y token_type "bearer"
    res_c7 = _login(client, "ana@example.com", "AnaPassword1")
    assert res_c7.status_code == 200
    tokens_ana = res_c7.json()
    assert "access_token" in tokens_ana
    assert "refresh_token" in tokens_ana
    assert tokens_ana["token_type"] == "bearer"
    ana_access = tokens_ana["access_token"]
    ana_refresh = tokens_ana["refresh_token"]

    # Caso 8: GET /auth/me sin token -> 401 y cabecera WWW-Authenticate: Bearer
    res_c8 = client.get("/api/v1/auth/me")
    assert res_c8.status_code == 401
    assert res_c8.headers.get("WWW-Authenticate") == "Bearer"

    # Caso 9: GET /auth/me con el token alterado en un carácter -> 401
    ultimo_char = "a" if ana_access[-1] != "a" else "b"
    token_alterado = ana_access[:-1] + ultimo_char
    res_c9 = client.get("/api/v1/auth/me", headers=_auth_header(token_alterado))
    assert res_c9.status_code == 401

    # Caso 10: GET /auth/me usando el refresh_token como Bearer -> 401
    res_c10 = client.get("/api/v1/auth/me", headers=_auth_header(ana_refresh))
    assert res_c10.status_code == 401

    # Cargar autor y categoría con el token del bibliotecario
    res_autor = client.post(
        "/api/v1/autores",
        headers=_auth_header(biblio_token),
        json={
            "nombre": "Gabriel Garcia Marquez",
            "nacionalidad": "Colombia",
            "anio_nacimiento": 1927,
        },
    )
    assert res_autor.status_code == 201
    autor_id = res_autor.json()["id"]

    res_cat = client.post(
        "/api/v1/categorias",
        headers=_auth_header(biblio_token),
        json={"nombre": "Novela", "descripcion": "Narrativa extensa"},
    )
    assert res_cat.status_code == 201
    cat_id = res_cat.json()["id"]

    # Caso 11: GET /libros sin token -> 200 con items, total, skip y limit
    res_c11 = client.get("/api/v1/libros")
    assert res_c11.status_code == 200
    body_c11 = res_c11.json()
    assert set(body_c11.keys()) >= {"items", "total", "skip", "limit"}

    # Caso 12: POST /libros con token de Ana -> 403
    libro_payload = {
        "titulo": "Cien Anios De Soledad",
        "isbn": "9780307474728",
        "anio_publicacion": 1967,
        "ejemplares": 4,
        "autor_id": autor_id,
        "categoria_ids": [cat_id],
    }
    res_c12 = client.post(
        "/api/v1/libros",
        headers=_auth_header(ana_access),
        json=libro_payload,
    )
    assert res_c12.status_code == 403

    # Caso 13: POST /libros con token del bibliotecario -> 201
    res_c13 = client.post(
        "/api/v1/libros",
        headers=_auth_header(biblio_token),
        json=libro_payload,
    )
    assert res_c13.status_code == 201
    libro1_id = res_c13.json()["id"]

    # Crear un segundo libro para pruebas de préstamos adicionales
    res_libro2 = client.post(
        "/api/v1/libros",
        headers=_auth_header(biblio_token),
        json={
            "titulo": "El Amor En Los Tiempos Del Colera",
            "isbn": "9780307387264",
            "anio_publicacion": 1985,
            "ejemplares": 3,
            "autor_id": autor_id,
            "categoria_ids": [cat_id],
        },
    )
    assert res_libro2.status_code == 201
    libro2_id = res_libro2.json()["id"]

    # Caso 14: DELETE /libros/{id} con token del bibliotecario -> 403
    res_c14 = client.delete(
        f"/api/v1/libros/{libro1_id}",
        headers=_auth_header(biblio_token),
    )
    assert res_c14.status_code == 403

    # Caso 15: El bibliotecario registra un préstamo a Ana -> 201 y registrado_por_id = id del bibliotecario
    res_c15 = client.post(
        "/api/v1/prestamos",
        headers=_auth_header(biblio_token),
        json={"libro_id": libro1_id, "socio_id": ana_socio_id, "dias": 14},
    )
    assert res_c15.status_code == 201
    prestamo_ana = res_c15.json()
    assert prestamo_ana["registrado_por_id"] == biblio_id

    # Caso 16: El bibliotecario registra un préstamo a Luis -> 201
    res_c16 = client.post(
        "/api/v1/prestamos",
        headers=_auth_header(biblio_token),
        json={"libro_id": libro1_id, "socio_id": luis_socio_id, "dias": 14},
    )
    assert res_c16.status_code == 201
    prestamo_luis_id = res_c16.json()["id"]

    # Caso 17: GET /prestamos con token de Ana -> Solo el préstamo de Ana (total: 1)
    res_c17 = client.get("/api/v1/prestamos", headers=_auth_header(ana_access))
    assert res_c17.status_code == 200
    assert res_c17.json()["total"] == 1
    assert res_c17.json()["items"][0]["socio_id"] == ana_socio_id

    # Caso 18: GET /prestamos?socio_id={Luis} con token de Ana -> Solo los préstamos de Ana
    res_c18 = client.get(
        f"/api/v1/prestamos?socio_id={luis_socio_id}",
        headers=_auth_header(ana_access),
    )
    assert res_c18.status_code == 200
    assert res_c18.json()["total"] == 1
    assert all(
        item["socio_id"] == ana_socio_id for item in res_c18.json()["items"]
    )

    # Caso 19: GET /prestamos/{id del préstamo de Luis} con token de Ana -> 404
    res_c19 = client.get(
        f"/api/v1/prestamos/{prestamo_luis_id}",
        headers=_auth_header(ana_access),
    )
    assert res_c19.status_code == 404

    # Caso 20: PATCH /socios/me con { "activo": false } con token de Ana -> 422
    res_c20 = client.patch(
        "/api/v1/socios/me",
        headers=_auth_header(ana_access),
        json={"activo": False},
    )
    assert res_c20.status_code == 422

    # Caso 21: POST /auth/refresh con el refresh de Ana -> 200 con un par nuevo
    res_c21 = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": ana_refresh},
    )
    assert res_c21.status_code == 200
    nuevos_tokens_ana = res_c21.json()
    assert "access_token" in nuevos_tokens_ana
    assert "refresh_token" in nuevos_tokens_ana
    ana_refresh_2 = nuevos_tokens_ana["refresh_token"]

    # Caso 22: POST /auth/refresh otra vez con el refresh anterior -> 401 y todos los refresh de Ana quedan revocados
    res_c22 = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": ana_refresh},
    )
    assert res_c22.status_code == 401
    # Verificar que el segundo refresh de Ana también quedó revocado por seguridad
    res_c22_revocado = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": ana_refresh_2},
    )
    assert res_c22_revocado.status_code == 401

    # Caso 23: Login de Ana, logout y luego refresh con ese token -> 401
    limiter.reset()
    res_login_ana_23 = _login(client, "ana@example.com", "AnaPassword1")
    assert res_login_ana_23.status_code == 200
    ana_access = res_login_ana_23.json()["access_token"]
    ana_refresh_23 = res_login_ana_23.json()["refresh_token"]

    res_logout = client.post(
        "/api/v1/auth/logout",
        headers=_auth_header(ana_access),
        json={"refresh_token": ana_refresh_23},
    )
    assert res_logout.status_code == 204

    res_c23 = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": ana_refresh_23},
    )
    assert res_c23.status_code == 401

    # Caso 24: Luis falla el login 5 veces y luego usa la contraseña correcta -> 423 cuenta bloqueada
    limiter.reset()
    res_login_luis_prev = _login(client, "luis@example.com", "LuisPassword1")
    assert res_login_luis_prev.status_code == 200
    luis_access = res_login_luis_prev.json()["access_token"]

    for _ in range(5):
        r_fail = _login(client, "luis@example.com", "ClaveIncorrecta1")
        assert r_fail.status_code == 401

    res_c24 = _login(client, "luis@example.com", "LuisPassword1")
    assert res_c24.status_code == 423
    assert "bloqueada" in res_c24.json()["detail"].lower()

    # Caso 26: El admin desactiva a Luis; Luis usa su access token vigente en /auth/me -> 403 "Usuario inactivo"
    res_desactivar_luis = client.patch(
        f"/api/v1/usuarios/{luis_user_id}/activo",
        headers=_auth_header(admin_token),
        json={"activo": False},
    )
    assert res_desactivar_luis.status_code == 200

    res_c26 = client.get(
        "/api/v1/auth/me",
        headers=_auth_header(luis_access),
    )
    assert res_c26.status_code == 403
    assert res_c26.json()["detail"] == "Usuario inactivo"

    # Caso 27: El admin se cambia a sí mismo el rol a socio -> 422
    res_c27 = client.patch(
        f"/api/v1/usuarios/{admin.id}/rol",
        headers=_auth_header(admin_token),
        json={"rol": "socio"},
    )
    assert res_c27.status_code == 422

    # Caso 28: GET /reportes/resumen con token de Ana / del bibliotecario -> 403 / 200
    res_c28_ana = client.get(
        "/api/v1/reportes/resumen",
        headers=_auth_header(ana_access),
    )
    assert res_c28_ana.status_code == 403

    res_c28_biblio = client.get(
        "/api/v1/reportes/resumen",
        headers=_auth_header(biblio_token),
    )
    assert res_c28_biblio.status_code == 200

    # Caso 29: Préstamo a Ana con fecha_prestamo de hace 20 días y dias: 7; devolverlo hoy (multa 6.5) y luego Ana pide otro libro -> 422 "El socio tiene multas pendientes"
    hace_20_dias = (date.today() - timedelta(days=20)).isoformat()
    res_prestamo_29 = client.post(
        "/api/v1/prestamos",
        headers=_auth_header(biblio_token),
        json={
            "libro_id": libro2_id,
            "socio_id": ana_socio_id,
            "fecha_prestamo": hace_20_dias,
            "dias": 7,
        },
    )
    assert res_prestamo_29.status_code == 201
    prestamo_29_id = res_prestamo_29.json()["id"]

    res_dev_29 = client.post(
        f"/api/v1/prestamos/{prestamo_29_id}/devolucion",
        headers=_auth_header(biblio_token),
        json={"fecha_devolucion": date.today().isoformat()},
    )
    assert res_dev_29.status_code == 200
    assert Decimal(str(res_dev_29.json()["multa"])) == Decimal("6.50")

    res_c29 = client.post(
        "/api/v1/prestamos",
        headers=_auth_header(biblio_token),
        json={
            "libro_id": libro2_id,
            "socio_id": ana_socio_id,
            "dias": 7,
        },
    )
    assert res_c29.status_code == 422
    assert res_c29.json()["detail"] == "El socio tiene multas pendientes"

    # Caso 30: POST /prestamos/{id}/pago-multa y repetir el préstamo del caso 29 -> 200 y luego 201
    res_c30_pago = client.post(
        f"/api/v1/prestamos/{prestamo_29_id}/pago-multa",
        headers=_auth_header(biblio_token),
    )
    assert res_c30_pago.status_code == 200
    assert res_c30_pago.json()["multa_pagada"] is True

    # Pagar de nuevo da 409
    res_pago_repetido = client.post(
        f"/api/v1/prestamos/{prestamo_29_id}/pago-multa",
        headers=_auth_header(biblio_token),
    )
    assert res_pago_repetido.status_code == 409

    res_c30_prestamo = client.post(
        "/api/v1/prestamos",
        headers=_auth_header(biblio_token),
        json={
            "libro_id": libro2_id,
            "socio_id": ana_socio_id,
            "dias": 7,
        },
    )
    assert res_c30_prestamo.status_code == 201


def test_caso_25_rate_limiting_login(client: TestClient):
    """Caso 25: 11 peticiones de login en menos de un minuto -> La 11.ª responde 429."""
    # Debe ejecutarse DESPUÉS del flujo completo: el decorador @limiter.limit
    # consulta el storage global (de sesión) en cada petición.
    assert (
        _login(client, "admin@biblioteca.com", "Admin1234").status_code == 200
    ), "Ejecuta la suite completa en orden: el caso 25 necesita los datos previos"

    limiter.reset()

    for _ in range(10):
        r = _login(client, "noexiste@example.com", "Clave1234")
        assert r.status_code == 401

    res_11 = _login(client, "noexiste@example.com", "Clave1234")
    assert res_11.status_code == 429


def test_endpoints_adicionales_y_reportes(
    client: TestClient, db_session: Session
):
    """Prueba endpoints de /socios/me, /usuarios, /reportes, /autores, /categorias y /auth/me/password."""
    admin_root = client.get("/")
    assert admin_root.status_code == 200

    admin_login = _login(client, "admin@biblioteca.com", "Admin1234")
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    biblio_login = _login(client, "biblio@biblioteca.com", "Biblio1234")
    assert biblio_login.status_code == 200
    biblio_token = biblio_login.json()["access_token"]
    ana_login = _login(client, "ana@example.com", "AnaPassword1")
    assert ana_login.status_code == 200
    ana_token = ana_login.json()["access_token"]

    # GET y PATCH /socios/me, /socios/me/prestamos, /socios/me/multas
    res_me = client.get("/api/v1/socios/me", headers=_auth_header(ana_token))
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "ana@example.com"

    res_patch_me = client.patch(
        "/api/v1/socios/me",
        headers=_auth_header(ana_token),
        json={"nombre": "Ana Maria Torres", "telefono": "3009998877"},
    )
    assert res_patch_me.status_code == 200
    assert res_patch_me.json()["nombre"] == "Ana Maria Torres"

    res_mis_prestamos = client.get(
        "/api/v1/socios/me/prestamos?estado=activo",
        headers=_auth_header(ana_token),
    )
    assert res_mis_prestamos.status_code == 200
    assert res_mis_prestamos.json()["total"] >= 1

    res_mis_multas = client.get(
        "/api/v1/socios/me/multas",
        headers=_auth_header(ana_token),
    )
    assert res_mis_multas.status_code == 200
    assert "total_adeudado" in res_mis_multas.json()

    # GET /usuarios con filtros (admin)
    res_usuarios = client.get(
        "/api/v1/usuarios?rol=socio&activo=true",
        headers=_auth_header(admin_token),
    )
    assert res_usuarios.status_code == 200
    assert res_usuarios.json()["total"] >= 1

    # Cambiar password en /auth/me/password
    res_pwd = client.patch(
        "/api/v1/auth/me/password",
        headers=_auth_header(ana_token),
        json={
            "password_actual": "AnaPassword1",
            "password_nueva": "AnaNuevaClave2",
        },
    )
    assert res_pwd.status_code == 200

    # Reportes con bibliotecario
    for ruta in (
        "/api/v1/reportes/libros-mas-prestados",
        "/api/v1/reportes/categorias",
        "/api/v1/reportes/prestamos-vencidos",
        "/api/v1/reportes/socios-con-multas",
        "/api/v1/reportes/autores",
        "/api/v1/reportes/resumen",
    ):
        r = client.get(ruta, headers=_auth_header(biblio_token))
        assert r.status_code == 200

    # Catálogo público: autores, categorías, libros con filtros
    assert client.get("/api/v1/autores?nacionalidad=Col").status_code == 200
    assert client.get("/api/v1/autores/1").status_code == 200
    assert client.get("/api/v1/autores/1/libros").status_code == 200
    assert client.get("/api/v1/categorias").status_code == 200
    assert client.get("/api/v1/categorias/1").status_code == 200
    assert (
        client.get(
            "/api/v1/libros?buscar=Cien&autor=Gabriel&categoria_id=1&desde=1900&hasta=2000&orden=-anio"
        ).status_code
        == 200
    )
    assert client.get("/api/v1/libros/1").status_code == 200

    # Gestión de socios por bibliotecario
    assert (
        client.get(
            "/api/v1/socios?activo=true", headers=_auth_header(biblio_token)
        ).status_code
        == 200
    )
    assert (
        client.get(
            "/api/v1/socios/1", headers=_auth_header(biblio_token)
        ).status_code
        == 200
    )
    assert (
        client.get(
            "/api/v1/socios/1/prestamos", headers=_auth_header(biblio_token)
        ).status_code
        == 200
    )

    # Crear y eliminar categoría/autor con admin
    res_nueva_cat = client.post(
        "/api/v1/categorias",
        headers=_auth_header(biblio_token),
        json={"nombre": "Poesia", "descripcion": "Versos"},
    )
    assert res_nueva_cat.status_code == 201
    nueva_cat_id = res_nueva_cat.json()["id"]

    res_patch_cat = client.patch(
        f"/api/v1/categorias/{nueva_cat_id}",
        headers=_auth_header(biblio_token),
        json={"descripcion": "Obras en verso"},
    )
    assert res_patch_cat.status_code == 200

    res_del_cat = client.delete(
        f"/api/v1/categorias/{nueva_cat_id}",
        headers=_auth_header(admin_token),
    )
    assert res_del_cat.status_code == 204

    res_nuevo_autor = client.post(
        "/api/v1/autores",
        headers=_auth_header(biblio_token),
        json={"nombre": "Jorge Luis Borges", "nacionalidad": "Argentina"},
    )
    assert res_nuevo_autor.status_code == 201
    nuevo_autor_id = res_nuevo_autor.json()["id"]

    res_patch_autor = client.patch(
        f"/api/v1/autores/{nuevo_autor_id}",
        headers=_auth_header(biblio_token),
        json={"anio_nacimiento": 1899},
    )
    assert res_patch_autor.status_code == 200

    res_del_autor = client.delete(
        f"/api/v1/autores/{nuevo_autor_id}",
        headers=_auth_header(admin_token),
    )
    assert res_del_autor.status_code == 204

    # Script crear_admin idempotente
    admin_creado = crear_administrador(
        email="admin@biblioteca.com",
        nombre="Admin Biblioteca",
        password="Admin1234",
    )
    assert admin_creado is not None
