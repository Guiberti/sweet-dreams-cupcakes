from werkzeug.security import check_password_hash, generate_password_hash

from ..db import get_db
from ..services.validacoes import somente_digitos


class EmailJaCadastrado(ValueError):
    pass


class Usuario:
    TIPOS = ("CLIENTE", "ADMIN", "ENTREGADOR")

    @staticmethod
    def criar(nome, email, senha, telefone=None, tipo="CLIENTE") -> int:
        if tipo not in Usuario.TIPOS:
            raise ValueError("Tipo de usuário inválido.")
        db = get_db()
        email = email.strip().lower()
        if Usuario.buscar_por_email(email):
            raise EmailJaCadastrado("Este e-mail já está cadastrado. Faça login ou recupere sua senha.")
        cur = db.execute(
            "INSERT INTO usuario (nome, email, senha_hash, telefone, tipo) VALUES (?,?,?,?,?)",
            (nome.strip(), email, generate_password_hash(senha), somente_digitos(telefone) or None, tipo),
        )
        db.commit()
        return cur.lastrowid

    @staticmethod
    def buscar_por_email(email):
        return get_db().execute("SELECT * FROM usuario WHERE email = ?", (email.strip().lower(),)).fetchone()

    @staticmethod
    def buscar_por_id(usuario_id):
        return get_db().execute("SELECT * FROM usuario WHERE id = ?", (usuario_id,)).fetchone()

    @staticmethod
    def autenticar(email, senha):
        usuario = Usuario.buscar_por_email(email or "")
        if usuario and usuario["ativo"] and check_password_hash(usuario["senha_hash"], senha or ""):
            return usuario
        return None

    @staticmethod
    def listar_por_tipo(tipo):
        return get_db().execute(
            "SELECT * FROM usuario WHERE tipo = ? AND ativo = 1 ORDER BY nome", (tipo,)
        ).fetchall()

    @staticmethod
    def atualizar_perfil(usuario_id, nome, telefone):
        db = get_db()
        db.execute("UPDATE usuario SET nome = ?, telefone = ? WHERE id = ?",
                   (nome.strip(), somente_digitos(telefone) or None, usuario_id))
        db.commit()


class Endereco:
    CAMPOS = ("apelido", "cep", "logradouro", "numero", "complemento", "bairro", "cidade", "uf")

    @staticmethod
    def validar(dados: dict) -> list[str]:
        erros = []
        if len(somente_digitos(dados.get("cep"))) != 8:
            erros.append("CEP deve ter 8 dígitos.")
        for campo, rotulo in (("logradouro", "Rua"), ("numero", "Número"), ("bairro", "Bairro"), ("cidade", "Cidade")):
            if not (dados.get(campo) or "").strip():
                erros.append(f"O campo {rotulo} é obrigatório.")
        if len((dados.get("uf") or "").strip()) != 2:
            erros.append("UF deve ter 2 letras (ex.: PR).")
        return erros

    @staticmethod
    def criar(usuario_id, dados: dict) -> int:
        db = get_db()
        primeiro = db.execute("SELECT COUNT(*) FROM endereco WHERE usuario_id = ?", (usuario_id,)).fetchone()[0] == 0
        cur = db.execute(
            """INSERT INTO endereco (usuario_id, apelido, cep, logradouro, numero, complemento, bairro, cidade, uf, principal)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (usuario_id, (dados.get("apelido") or "Casa").strip(), somente_digitos(dados["cep"]),
             dados["logradouro"].strip(), dados["numero"].strip(), (dados.get("complemento") or "").strip() or None,
             dados["bairro"].strip(), dados["cidade"].strip(), dados["uf"].strip().upper(), 1 if primeiro else 0),
        )
        db.commit()
        return cur.lastrowid

    @staticmethod
    def listar(usuario_id):
        return get_db().execute(
            "SELECT * FROM endereco WHERE usuario_id = ? ORDER BY principal DESC, id", (usuario_id,)
        ).fetchall()

    @staticmethod
    def buscar(endereco_id, usuario_id):
        return get_db().execute(
            "SELECT * FROM endereco WHERE id = ? AND usuario_id = ?", (endereco_id, usuario_id)
        ).fetchone()

    @staticmethod
    def excluir(endereco_id, usuario_id):
        db = get_db()
        db.execute("DELETE FROM endereco WHERE id = ? AND usuario_id = ?", (endereco_id, usuario_id))
        db.commit()

    @staticmethod
    def definir_principal(endereco_id, usuario_id):
        db = get_db()
        db.execute("UPDATE endereco SET principal = 0 WHERE usuario_id = ?", (usuario_id,))
        db.execute("UPDATE endereco SET principal = 1 WHERE id = ? AND usuario_id = ?", (endereco_id, usuario_id))
        db.commit()

    @staticmethod
    def formatar(e) -> str:
        comp = f" - {e['complemento']}" if e["complemento"] else ""
        cep = f"{e['cep'][:5]}-{e['cep'][5:]}"
        return f"{e['logradouro']}, {e['numero']}{comp} - {e['bairro']}, {e['cidade']}/{e['uf']} - CEP {cep}"
