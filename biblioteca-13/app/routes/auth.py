from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.controllers import auth as auth_controller
from app.core.dependencies import CurrentUser, SessionDep
from app.core.security import limiter
from app.schemas.auth import (
    CambiarPasswordPeticion,
    RefreshPeticion,
    TokenRespuesta,
    UsuarioRegistro,
)
from app.schemas.usuario import UsuarioRespuesta

RESPUESTAS_ERROR = {
    401: {"description": "No autenticado o token inválido"},
    403: {"description": "Sin permisos o usuario inactivo"},
    404: {"description": "Recurso no encontrado"},
}

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
    responses=RESPUESTAS_ERROR,
)


@router.post(
    "/registro",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo socio",
)
@limiter.limit("5/minute")
def registrar(
    request: Request,
    datos: UsuarioRegistro,
    db: SessionDep,
):
    return auth_controller.registrar_usuario(db, datos)


@router.post(
    "/login",
    response_model=TokenRespuesta,
    summary="Iniciar sesión y obtener tokens JWT",
)
@limiter.limit("10/minute")
def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
):
    return auth_controller.iniciar_sesion(
        db, form_data.username, form_data.password
    )


@router.post(
    "/refresh",
    response_model=TokenRespuesta,
    summary="Renovar access token mediante rotación de refresh token",
)
def refresh_token_endpoint(datos: RefreshPeticion, db: SessionDep):
    return auth_controller.renovar_token(db, datos.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar sesión revocando el refresh token",
)
def logout(datos: RefreshPeticion, db: SessionDep) -> None:
    auth_controller.cerrar_sesion(db, datos.refresh_token)


@router.get(
    "/me",
    response_model=UsuarioRespuesta,
    summary="Obtener datos del usuario autenticado",
)
def obtener_me(usuario: CurrentUser):
    return usuario


@router.patch(
    "/me/password",
    response_model=UsuarioRespuesta,
    summary="Cambiar contraseña del usuario autenticado",
)
def cambiar_mi_password(
    datos: CambiarPasswordPeticion,
    usuario: CurrentUser,
    db: SessionDep,
):
    return auth_controller.cambiar_password(db, usuario, datos)
