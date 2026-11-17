# conexao com o sqlite + comando `flask init-db`
import sqlite3
from pathlib import Path

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA = BASE_DIR / "database" / "schema.sql"
SEED = BASE_DIR / "database" / "seed.sql"

USUARIOS_DEMO = [
    ("Administrador Sweet Dreams", "admin@sweetdreams.com", "Admin@123", "41999990001", "ADMIN"),
    ("Carlos Entregador", "entregador@sweetdreams.com", "Entrega@123", "41999990002", "ENTREGADOR"),
    ("Cliente de Teste", "cliente@teste.com", "Cliente@123", "41999990003", "CLIENTE"),
]


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(com_dados_demo: bool = True):
    db = get_db()
    db.executescript(SCHEMA.read_text(encoding="utf-8"))
    if com_dados_demo:
        db.executescript(SEED.read_text(encoding="utf-8"))
        for nome, email, senha, tel, tipo in USUARIOS_DEMO:
            db.execute(
                "INSERT INTO usuario (nome, email, senha_hash, telefone, tipo) VALUES (?,?,?,?,?)",
                (nome, email, generate_password_hash(senha), tel, tipo),
            )
        db.execute(
            """INSERT INTO endereco (usuario_id, apelido, cep, logradouro, numero, bairro, cidade, uf, principal)
               VALUES (3, 'Casa', '80010000', 'Rua XV de Novembro', '100', 'Centro', 'Curitiba', 'PR', 1)"""
        )
    db.commit()


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Banco de dados criado com dados de demonstração.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
