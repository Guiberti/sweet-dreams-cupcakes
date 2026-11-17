from ..db import get_db


class Categoria:
    @staticmethod
    def listar():
        return get_db().execute("SELECT * FROM categoria ORDER BY id").fetchall()

    @staticmethod
    def buscar(categoria_id):
        return get_db().execute("SELECT * FROM categoria WHERE id = ?", (categoria_id,)).fetchone()


class Produto:
    @staticmethod
    def listar(categoria_id=None, busca=None, somente_ativos=True):
        sql = ("SELECT p.*, c.nome AS categoria_nome FROM produto p "
               "JOIN categoria c ON c.id = p.categoria_id WHERE 1=1")
        params = []
        if somente_ativos:
            sql += " AND p.ativo = 1"
        if categoria_id:
            sql += " AND p.categoria_id = ?"
            params.append(categoria_id)
        if busca:
            sql += " AND (p.nome LIKE ? OR p.descricao LIKE ?)"
            params += [f"%{busca}%", f"%{busca}%"]
        sql += " ORDER BY (p.estoque = 0), p.categoria_id, p.nome"
        return get_db().execute(sql, params).fetchall()

    @staticmethod
    def buscar(produto_id):
        return get_db().execute(
            "SELECT p.*, c.nome AS categoria_nome FROM produto p JOIN categoria c ON c.id = p.categoria_id "
            "WHERE p.id = ?", (produto_id,)
        ).fetchone()

    @staticmethod
    def validar(dados: dict) -> list[str]:
        erros = []
        if len((dados.get("nome") or "").strip()) < 3:
            erros.append("Nome do produto deve ter pelo menos 3 caracteres.")
        try:
            if float(str(dados.get("preco", "")).replace(",", ".")) <= 0:
                erros.append("Preço deve ser maior que zero.")
        except ValueError:
            erros.append("Preço inválido.")
        try:
            if int(dados.get("estoque", "")) < 0:
                erros.append("Estoque não pode ser negativo.")
        except ValueError:
            erros.append("Estoque deve ser um número inteiro.")
        if not Categoria.buscar(dados.get("categoria_id")):
            erros.append("Selecione uma categoria válida.")
        return erros

    @staticmethod
    def _valores(dados):
        return (
            int(dados["categoria_id"]), dados["nome"].strip(), (dados.get("descricao") or "").strip(),
            round(float(str(dados["preco"]).replace(",", ".")), 2), int(dados["estoque"]),
            int(dados["calorias"]) if str(dados.get("calorias") or "").isdigit() else None,
            dados.get("cor") or "#FF85C0", (dados.get("destaque") or "").strip().upper() or None,
            1 if dados.get("ativo", "1") in ("1", "on", 1, True) else 0,
        )

    @staticmethod
    def criar(dados: dict) -> int:
        db = get_db()
        cur = db.execute(
            "INSERT INTO produto (categoria_id, nome, descricao, preco, estoque, calorias, cor, destaque, ativo) "
            "VALUES (?,?,?,?,?,?,?,?,?)", Produto._valores(dados))
        db.commit()
        return cur.lastrowid

    @staticmethod
    def atualizar(produto_id, dados: dict):
        db = get_db()
        db.execute(
            "UPDATE produto SET categoria_id=?, nome=?, descricao=?, preco=?, estoque=?, calorias=?, cor=?, "
            "destaque=?, ativo=? WHERE id=?", (*Produto._valores(dados), produto_id))
        db.commit()

    @staticmethod
    def desativar(produto_id):
        # nao apaga de verdade pq o produto pode estar em pedidos antigos
        db = get_db()
        db.execute("UPDATE produto SET ativo = 0 WHERE id = ?", (produto_id,))
        db.commit()
