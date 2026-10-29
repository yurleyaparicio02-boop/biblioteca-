import getpass

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hashear_password
from app.models.usuario import RolUsuario, Usuario
from app.schemas.auth import validar_reglas_password


def crear_administrador(
    email: str | None = None,
    nombre: str | None = None,
    password: str | None = None,
) -> Usuario | None:
    print("=== Creación del Primer Administrador ===")
    if email is None:
        email = input("Correo electrónico del admin: ").strip().lower()
    else:
        email = email.strip().lower()

    if nombre is None:
        nombre = input("Nombre completo: ").strip().title()
    else:
        nombre = nombre.strip().title()

    if password is None:
        password = getpass.getpass("Contraseña: ")
        confirmar_password = getpass.getpass("Confirme la contraseña: ")
        if password != confirmar_password:
            print("Error: Las contraseñas no coinciden.")
            return None

    try:
        validar_reglas_password(password)
        if len(password) < 8 or len(password) > 64:
            raise ValueError("La contraseña debe tener entre 8 y 64 caracteres")
    except ValueError as e:
        print(f"Error: {e}")
        return None

    db = SessionLocal()
    try:
        existente = db.scalar(select(Usuario).where(Usuario.email == email))
        if existente:
            print(f"El usuario con correo {email} ya existe en el sistema.")
            return existente

        nuevo_admin = Usuario(
            email=email,
            nombre=nombre,
            password_hash=hashear_password(password),
            rol=RolUsuario.admin,
            activo=True,
        )
        db.add(nuevo_admin)
        db.commit()
        db.refresh(nuevo_admin)
        print(f"¡Administrador {email} creado exitosamente!")
        return nuevo_admin
    except Exception as e:
        db.rollback()
        print(f"Error al crear el administrador: {e}")
        return None
    finally:
        db.close()


if __name__ == "__main__":
    crear_administrador()
