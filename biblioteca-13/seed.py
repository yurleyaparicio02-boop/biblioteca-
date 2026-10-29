"""Pobla la base de datos con datos de ejemplo.

Es idempotente: busca cada registro por su clave natural (nombre, ISBN o email)
y solo lo crea si no existe. Se puede ejecutar varias veces sin duplicar nada.

Uso:
    .\\.venv\\Scripts\\python.exe seed.py
"""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Autor, Categoria, Libro, Prestamo, Socio

HOY = date.today()

AUTORES = [
    {"nombre": "Gabriel Garcia Marquez", "nacionalidad": "Colombia", "anio_nacimiento": 1927},
    {"nombre": "Isabel Allende", "nacionalidad": "Chile", "anio_nacimiento": 1942},
    {"nombre": "Jorge Luis Borges", "nacionalidad": "Argentina", "anio_nacimiento": 1899},
    {"nombre": "Mario Vargas Llosa", "nacionalidad": "Peru", "anio_nacimiento": 1936},
    {"nombre": "Laura Esquivel", "nacionalidad": "Mexico", "anio_nacimiento": 1950},
    {"nombre": "Julio Cortazar", "nacionalidad": "Argentina", "anio_nacimiento": 1914},
    {"nombre": "J. K. Rowling", "nacionalidad": "Reino Unido", "anio_nacimiento": 1965},
    {"nombre": "George Orwell", "nacionalidad": "Reino Unido", "anio_nacimiento": 1903},
    {"nombre": "Antoine de Saint-Exupery", "nacionalidad": "Francia", "anio_nacimiento": 1900},
    {"nombre": "Robert C. Martin", "nacionalidad": "Estados Unidos", "anio_nacimiento": 1952},
]

CATEGORIAS = [
    {"nombre": "Novela", "descripcion": "Narrativa extensa de ficcion"},
    {"nombre": "Cuento", "descripcion": "Relatos breves de ficcion"},
    {"nombre": "Ciencia ficcion", "descripcion": "Ficcion especulativa y futurista"},
    {"nombre": "Fantasia", "descripcion": "Mundos imaginarios y magia"},
    {"nombre": "Poesia", "descripcion": "Obras en verso"},
    {"nombre": "Tecnologia", "descripcion": "Informatica, software y ensayo tecnico"},
    {"nombre": "Infantil", "descripcion": "Literatura para ninos y jovenes"},
    {"nombre": "Historia", "descripcion": "Ensayo historico y divulgacion"},
]

# (titulo, isbn, anio, ejemplares, autor, [categorias])
LIBROS = [
    ("Cien anios de soledad", "9780307474728", 1967, 4, "Gabriel Garcia Marquez", ["Novela"]),
    ("El amor en los tiempos del colera", "9780307387264", 1985, 3, "Gabriel Garcia Marquez", ["Novela"]),
    ("Cronica de una muerte anunciada", "9781400034956", 1981, 2, "Gabriel Garcia Marquez", ["Novela"]),
    ("La casa de los espiritus", "9781501117019", 1982, 3, "Isabel Allende", ["Novela", "Fantasia"]),
    ("Eva Luna", "9781501117026", 1987, 2, "Isabel Allende", ["Novela"]),
    ("Ficciones", "9780802130303", 1944, 3, "Jorge Luis Borges", ["Cuento", "Fantasia"]),
    ("El aleph", "9780142437889", 1949, 2, "Jorge Luis Borges", ["Cuento"]),
    ("La ciudad y los perros", "9788420471839", 1963, 2, "Mario Vargas Llosa", ["Novela"]),
    ("La fiesta del chivo", "9780312426392", 2000, 3, "Mario Vargas Llosa", ["Novela", "Historia"]),
    ("Como agua para chocolate", "9780385420174", 1989, 4, "Laura Esquivel", ["Novela", "Fantasia"]),
    ("Rayuela", "9780394752846", 1963, 2, "Julio Cortazar", ["Novela"]),
    ("Bestiario", "9788466331449", 1951, 1, "Julio Cortazar", ["Cuento"]),
    ("Harry Potter y la piedra filosofal", "9788478884452", 1997, 5, "J. K. Rowling", ["Fantasia", "Infantil"]),
    ("Harry Potter y la camara secreta", "9788478884957", 1998, 4, "J. K. Rowling", ["Fantasia", "Infantil"]),
    ("1984", "9780451524935", 1949, 4, "George Orwell", ["Novela", "Ciencia ficcion"]),
    ("Rebelion en la granja", "9780452284241", 1945, 3, "George Orwell", ["Novela"]),
    ("El principito", "9780156012195", 1943, 6, "Antoine de Saint-Exupery", ["Infantil"]),
    ("Clean Code", "9780132350884", 2008, 2, "Robert C. Martin", ["Tecnologia"]),
    ("Codigo limpio en Python", "9781098136349", 2022, 1, "Robert C. Martin", ["Tecnologia"]),
    ("Arquitectura limpia", "9780134494166", 2017, 2, "Robert C. Martin", ["Tecnologia"]),
]

# (nombre, email, telefono, activo)
SOCIOS = [
    ("Ana Torres", "ana.torres@example.com", "3001112233", True),
    ("Luis Ramirez", "luis.ramirez@example.com", "3002223344", True),
    ("Carla Mendoza", "carla.mendoza@example.com", "3003334455", True),
    ("Diego Herrera", "diego.herrera@example.com", "3004445566", True),
    ("Elena Pardo", "elena.pardo@example.com", "3005556677", True),
    ("Fabian Rojas", "fabian.rojas@example.com", "3006667788", True),
    ("Gloria Suarez", "gloria.suarez@example.com", "3007778899", True),
    ("Hector Leon", "hector.leon@example.com", "3008889900", False),
    ("Ines Cabrera", "ines.cabrera@example.com", "3009990011", True),
    ("Julian Vera", "julian.vera@example.com", "3010001122", True),
]

# (isbn, email socio, fecha_prestamo, fecha_limite, fecha_devolucion | None,
#  multa, multa_pagada)
PRESTAMOS = [
    # Devuelto a tiempo, sin multa
    ("9780307474728", "ana.torres@example.com", HOY - timedelta(days=40), HOY - timedelta(days=26), HOY - timedelta(days=28), "0.00", False),
    # Devuelto con retraso de 4 dias: multa de 2.00 (pendiente)
    ("9780451524935", "luis.ramirez@example.com", HOY - timedelta(days=35), HOY - timedelta(days=21), HOY - timedelta(days=17), "2.00", False),
    # Devuelto con retraso de 2 dias: multa de 1.00 (ya pagada)
    ("9788478884452", "carla.mendoza@example.com", HOY - timedelta(days=30), HOY - timedelta(days=16), HOY - timedelta(days=14), "1.00", True),
    # Devuelto sin multa
    ("9780156012195", "diego.herrera@example.com", HOY - timedelta(days=25), HOY - timedelta(days=11), HOY - timedelta(days=12), "0.00", False),
    # Activo dentro de plazo
    ("9780307387264", "elena.pardo@example.com", HOY - timedelta(days=5), HOY + timedelta(days=9), None, "0.00", False),
    # Activo dentro de plazo
    ("9780132350884", "fabian.rojas@example.com", HOY - timedelta(days=2), HOY + timedelta(days=12), None, "0.00", False),
    # Vencido hace 6 dias (todavia sin devolver, sin multa calculada)
    ("9780385420174", "gloria.suarez@example.com", HOY - timedelta(days=20), HOY - timedelta(days=6), None, "0.00", False),
    # Vencido hace 3 dias
    ("9788478884957", "ines.cabrera@example.com", HOY - timedelta(days=17), HOY - timedelta(days=3), None, "0.00", False),
    # Activo dentro de plazo
    ("9788420471839", "julian.vera@example.com", HOY - timedelta(days=1), HOY + timedelta(days=13), None, "0.00", False),
    # Activo dentro de plazo (segundo prestamo de Ana)
    ("9780142437889", "ana.torres@example.com", HOY - timedelta(days=3), HOY + timedelta(days=11), None, "0.00", False),
    # Activo dentro de plazo (segundo prestamo de Luis)
    ("9780802130303", "luis.ramirez@example.com", HOY - timedelta(days=8), HOY + timedelta(days=6), None, "0.00", False),
    # Devuelto a tiempo
    ("9780312426392", "carla.mendoza@example.com", HOY - timedelta(days=60), HOY - timedelta(days=46), HOY - timedelta(days=47), "0.00", False),
]


def obtener_o_crear(db, modelo, filtro, **valores):
    existente = db.scalar(select(modelo).filter_by(**filtro))
    if existente is not None:
        return existente, False
    nuevo = modelo(**filtro, **valores)
    db.add(nuevo)
    db.flush()
    return nuevo, True


def main() -> None:
    creados = {"autores": 0, "categorias": 0, "libros": 0, "socios": 0, "prestamos": 0}

    with SessionLocal() as db:
        autores: dict[str, Autor] = {}
        for datos in AUTORES:
            autor, nuevo = obtener_o_crear(
                db,
                Autor,
                {"nombre": datos["nombre"]},
                nacionalidad=datos["nacionalidad"],
                anio_nacimiento=datos["anio_nacimiento"],
            )
            autores[autor.nombre] = autor
            creados["autores"] += int(nuevo)

        categorias: dict[str, Categoria] = {}
        for datos in CATEGORIAS:
            categoria, nuevo = obtener_o_crear(
                db,
                Categoria,
                {"nombre": datos["nombre"]},
                descripcion=datos["descripcion"],
            )
            categorias[categoria.nombre] = categoria
            creados["categorias"] += int(nuevo)
        db.flush()

        libros: dict[str, Libro] = {}
        for titulo, isbn, anio, ejemplares, autor, nombres_categoria in LIBROS:
            libro, nuevo = obtener_o_crear(
                db,
                Libro,
                {"isbn": isbn},
                titulo=titulo,
                anio_publicacion=anio,
                ejemplares=ejemplares,
                autor=autores[autor],
            )
            categorias_libro = [categorias[n] for n in nombres_categoria]
            for categoria in categorias_libro:
                if categoria not in libro.categorias:
                    libro.categorias.append(categoria)
            libros[isbn] = libro
            creados["libros"] += int(nuevo)
        db.flush()

        socios: dict[str, Socio] = {}
        for nombre, email, telefono, activo in SOCIOS:
            socio, nuevo = obtener_o_crear(
                db,
                Socio,
                {"email": email},
                nombre=nombre,
                telefono=telefono,
                activo=activo,
            )
            socios[socio.email] = socio
            creados["socios"] += int(nuevo)
        db.flush()

        for isbn, email, fecha_prestamo, fecha_limite, devolucion, multa, pagada in PRESTAMOS:
            libro = libros[isbn]
            socio = socios[email]
            existe = db.scalar(
                select(Prestamo).filter_by(
                    libro_id=libro.id,
                    socio_id=socio.id,
                    fecha_prestamo=fecha_prestamo,
                )
            )
            if existe is not None:
                continue
            db.add(
                Prestamo(
                    libro_id=libro.id,
                    socio_id=socio.id,
                    fecha_prestamo=fecha_prestamo,
                    fecha_limite=fecha_limite,
                    fecha_devolucion=devolucion,
                    multa=Decimal(multa),
                    multa_pagada=pagada,
                )
            )
            creados["prestamos"] += 1

        db.commit()

    print("Datos creados:", creados)

    with SessionLocal() as db:
        for modelo in (Autor, Categoria, Libro, Socio, Prestamo):
            total = len(db.scalars(select(modelo)).all())
            print(f"{modelo.__tablename__}: {total}")


if __name__ == "__main__":
    main()
