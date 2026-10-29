class ErrorAplicacion(Exception):
    status_code = 400

    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)


class NoEncontrado(ErrorAplicacion):
    status_code = 404


class Conflicto(ErrorAplicacion):
    status_code = 409


class ReglaNegocio(ErrorAplicacion):
    status_code = 422


# Nuevas excepciones de seguridad (Fase 4)
class NoAutenticado(ErrorAplicacion):
    status_code = 401


class Prohibido(ErrorAplicacion):
    status_code = 403


class CuentaBloqueada(ErrorAplicacion):
    status_code = 423