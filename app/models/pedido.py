# regras do pedido: totais, baixa/devolucao de estoque e mudanca de status
import secrets

from ..db import get_db
from .cupom import Cupom


class PedidoInvalido(ValueError):
    pass


STATUS_ROTULOS = {
    "AGUARDANDO_PAGAMENTO": "Aguardando pagamento",
    "CONFIRMADO": "Pagamento confirmado",
    "EM_PREPARO": "Em preparo",
    "SAIU_PARA_ENTREGA": "Saiu para entrega",
    "ENTREGUE": "Entregue",
    "CANCELADO": "Cancelado",
}

# Máquina de estados: status atual -> próximos status permitidos
TRANSICOES = {
    "AGUARDANDO_PAGAMENTO": {"CONFIRMADO", "CANCELADO"},
    "CONFIRMADO": {"EM_PREPARO", "CANCELADO"},
    "EM_PREPARO": {"SAIU_PARA_ENTREGA", "ENTREGUE", "CANCELADO"},
    "SAIU_PARA_ENTREGA": {"ENTREGUE"},
    "ENTREGUE": set(),
    "CANCELADO": set(),
}


def transicao_permitida(atual: str, novo: str, tipo_entrega: str = "ENTREGA") -> bool:
    if novo not in TRANSICOES.get(atual, set()):
        return False
    # Pedido com entrega precisa passar por "Saiu para entrega"; retirada vai direto para "Entregue".
    if atual == "EM_PREPARO" and novo == "ENTREGUE" and tipo_entrega != "RETIRADA":
        return False
    if novo == "SAIU_PARA_ENTREGA" and tipo_entrega == "RETIRADA":
        return False
    return True


def calcular_totais(itens: list[dict], frete: float = 0.0, desconto: float = 0.0) -> dict:
    produtos = round(sum(i["preco"] * i["quantidade"] for i in itens), 2)
    desconto = round(min(desconto, produtos), 2)
    total = round(produtos + frete - desconto, 2)
    return {"produtos": produtos, "frete": round(frete, 2), "desconto": desconto, "total": total}


class Pedido:
    @staticmethod
    def criar(cliente_id: int, itens: list[dict], tipo_entrega: str, endereco_texto: str | None,
              frete: float, cupom_codigo: str | None = None, observacoes: str | None = None) -> int:
        # tudo numa transacao so: se faltar estoque de um item, nada e gravado
        if not itens:
            raise PedidoInvalido("Seu carrinho está vazio.")
        if tipo_entrega not in ("ENTREGA", "RETIRADA"):
            raise PedidoInvalido("Tipo de entrega inválido.")
        if tipo_entrega == "ENTREGA" and not endereco_texto:
            raise PedidoInvalido("Selecione um endereço de entrega.")

        db = get_db()
        try:
            linhas = []
            for item in itens:
                p = db.execute("SELECT * FROM produto WHERE id = ? AND ativo = 1", (item["produto_id"],)).fetchone()
                if not p:
                    raise PedidoInvalido("Um dos produtos do carrinho não está mais disponível.")
                if item["quantidade"] <= 0:
                    raise PedidoInvalido("Quantidade inválida.")
                if item["quantidade"] > p["estoque"]:
                    raise PedidoInvalido(f"Estoque insuficiente de {p['nome']}: restam {p['estoque']} unidade(s).")
                linhas.append({"produto_id": p["id"], "quantidade": item["quantidade"], "preco": p["preco"]})

            cupom_id, desconto = None, 0.0
            parcial = calcular_totais(linhas)
            if cupom_codigo:
                cupom, desconto = Cupom.validar(cupom_codigo, parcial["produtos"])
                cupom_id = cupom["id"]
            if tipo_entrega == "RETIRADA":
                frete = 0.0
            totais = calcular_totais(linhas, frete, desconto)

            cur = db.execute(
                """INSERT INTO pedido (numero, cliente_id, cupom_id, tipo_entrega, endereco_entrega, valor_produtos,
                   valor_frete, valor_desconto, valor_total, observacoes) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                ("TMP" + secrets.token_hex(6), cliente_id, cupom_id, tipo_entrega, endereco_texto,
                 totais["produtos"], totais["frete"], totais["desconto"], totais["total"],
                 (observacoes or "").strip()[:300] or None),
            )
            pedido_id = cur.lastrowid
            db.execute("UPDATE pedido SET numero = ? WHERE id = ?", (f"SD{pedido_id:06d}", pedido_id))
            for l in linhas:
                db.execute("INSERT INTO item_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?,?,?,?)",
                           (pedido_id, l["produto_id"], l["quantidade"], l["preco"]))
                db.execute("UPDATE produto SET estoque = estoque - ? WHERE id = ?", (l["quantidade"], l["produto_id"]))
            if cupom_id:
                db.execute("UPDATE cupom SET quantidade_disponivel = quantidade_disponivel - 1 WHERE id = ?", (cupom_id,))
            db.execute("INSERT INTO historico_status (pedido_id, status, usuario_id) VALUES (?, 'AGUARDANDO_PAGAMENTO', ?)",
                       (pedido_id, cliente_id))
            db.commit()
            return pedido_id
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def buscar(pedido_id):
        return get_db().execute(
            "SELECT p.*, u.nome AS cliente_nome, u.telefone AS cliente_telefone, e.nome AS entregador_nome, "
            "c.codigo AS cupom_codigo FROM pedido p JOIN usuario u ON u.id = p.cliente_id "
            "LEFT JOIN usuario e ON e.id = p.entregador_id LEFT JOIN cupom c ON c.id = p.cupom_id WHERE p.id = ?",
            (pedido_id,)).fetchone()

    @staticmethod
    def itens(pedido_id):
        return get_db().execute(
            "SELECT i.*, pr.nome, pr.cor, (i.quantidade * i.preco_unitario) AS subtotal FROM item_pedido i "
            "JOIN produto pr ON pr.id = i.produto_id WHERE i.pedido_id = ?", (pedido_id,)).fetchall()

    @staticmethod
    def historico(pedido_id):
        return get_db().execute(
            "SELECT h.*, u.nome AS usuario_nome FROM historico_status h LEFT JOIN usuario u ON u.id = h.usuario_id "
            "WHERE h.pedido_id = ? ORDER BY h.id", (pedido_id,)).fetchall()

    @staticmethod
    def listar_do_cliente(cliente_id):
        return get_db().execute(
            "SELECT * FROM pedido WHERE cliente_id = ? ORDER BY id DESC", (cliente_id,)).fetchall()

    @staticmethod
    def listar(status=None, entregador_id=None):
        sql = ("SELECT p.*, u.nome AS cliente_nome, e.nome AS entregador_nome FROM pedido p "
               "JOIN usuario u ON u.id = p.cliente_id LEFT JOIN usuario e ON e.id = p.entregador_id WHERE 1=1")
        params = []
        if status:
            sql += " AND p.status = ?"
            params.append(status)
        if entregador_id:
            sql += " AND p.entregador_id = ?"
            params.append(entregador_id)
        return get_db().execute(sql + " ORDER BY p.id DESC", params).fetchall()

    @staticmethod
    def atualizar_status(pedido_id: int, novo: str, usuario_id: int | None = None):
        db = get_db()
        pedido = db.execute("SELECT * FROM pedido WHERE id = ?", (pedido_id,)).fetchone()
        if not pedido:
            raise PedidoInvalido("Pedido não encontrado.")
        if not transicao_permitida(pedido["status"], novo, pedido["tipo_entrega"]):
            raise PedidoInvalido(
                f"Não é possível mudar de '{STATUS_ROTULOS[pedido['status']]}' para '{STATUS_ROTULOS.get(novo, novo)}'.")
        db.execute("UPDATE pedido SET status = ? WHERE id = ?", (novo, pedido_id))
        db.execute("INSERT INTO historico_status (pedido_id, status, usuario_id) VALUES (?,?,?)",
                   (pedido_id, novo, usuario_id))
        if novo == "CANCELADO":  # devolve o estoque
            for item in db.execute("SELECT * FROM item_pedido WHERE pedido_id = ?", (pedido_id,)).fetchall():
                db.execute("UPDATE produto SET estoque = estoque + ? WHERE id = ?", (item["quantidade"], item["produto_id"]))
        db.commit()

    @staticmethod
    def atribuir_entregador(pedido_id: int, entregador_id: int):
        db = get_db()
        ent = db.execute("SELECT * FROM usuario WHERE id = ? AND tipo = 'ENTREGADOR' AND ativo = 1",
                         (entregador_id,)).fetchone()
        if not ent:
            raise PedidoInvalido("Entregador inválido.")
        pedido = db.execute("SELECT * FROM pedido WHERE id = ?", (pedido_id,)).fetchone()
        if not pedido or pedido["tipo_entrega"] != "ENTREGA":
            raise PedidoInvalido("Somente pedidos com entrega podem receber entregador.")
        if pedido["status"] in ("ENTREGUE", "CANCELADO", "AGUARDANDO_PAGAMENTO"):
            raise PedidoInvalido("O pedido precisa estar pago e em andamento para receber entregador.")
        db.execute("UPDATE pedido SET entregador_id = ? WHERE id = ?", (entregador_id, pedido_id))
        db.commit()

    @staticmethod
    def resumo_vendas():
        db = get_db()
        validos = "status NOT IN ('CANCELADO', 'AGUARDANDO_PAGAMENTO')"
        geral = db.execute(f"SELECT COUNT(*) AS qtd, COALESCE(SUM(valor_total),0) AS total, "
                           f"COALESCE(AVG(valor_total),0) AS ticket FROM pedido WHERE {validos}").fetchone()
        por_status = db.execute("SELECT status, COUNT(*) AS qtd FROM pedido GROUP BY status").fetchall()
        top = db.execute(
            f"SELECT pr.nome, SUM(i.quantidade) AS qtd, SUM(i.quantidade * i.preco_unitario) AS receita "
            f"FROM item_pedido i JOIN pedido p ON p.id = i.pedido_id JOIN produto pr ON pr.id = i.produto_id "
            f"WHERE p.{validos} GROUP BY pr.id ORDER BY qtd DESC LIMIT 5").fetchall()
        return {"geral": geral, "por_status": por_status, "top": top}


class Pagamento:
    @staticmethod
    def registrar(pedido_id, forma, status, valor, **extra) -> int:
        db = get_db()
        cur = db.execute(
            "INSERT INTO pagamento (pedido_id, forma, status, valor, cartao_final, bandeira, codigo_transacao, "
            "pix_copia_cola, motivo_recusa) VALUES (?,?,?,?,?,?,?,?,?)",
            (pedido_id, forma, status, valor, extra.get("cartao_final"), extra.get("bandeira"),
             extra.get("codigo_transacao"), extra.get("pix_copia_cola"), extra.get("motivo")))
        db.commit()
        return cur.lastrowid

    @staticmethod
    def ultimo(pedido_id):
        return get_db().execute("SELECT * FROM pagamento WHERE pedido_id = ? ORDER BY id DESC LIMIT 1",
                                (pedido_id,)).fetchone()

    @staticmethod
    def aprovar_pix(pagamento_id):
        db = get_db()
        db.execute("UPDATE pagamento SET status = 'APROVADO', codigo_transacao = ? WHERE id = ?",
                   ("PIX" + secrets.token_hex(6).upper(), pagamento_id))
        db.commit()
