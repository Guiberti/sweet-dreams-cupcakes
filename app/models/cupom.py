from datetime import date

from ..db import get_db


class CupomInvalido(ValueError):
    pass


class Cupom:
    @staticmethod
    def calcular_desconto(tipo: str, valor: float, valor_produtos: float) -> float:
        if tipo == "PERCENTUAL":
            desconto = valor_produtos * valor / 100
        else:
            desconto = valor
        return round(min(desconto, valor_produtos), 2)

    @staticmethod
    def validar(codigo: str, valor_produtos: float, hoje: date | None = None, cliente_id: int | None = None):
        hoje = hoje or date.today()
        codigo = (codigo or "").strip().upper()
        if not codigo:
            raise CupomInvalido("Informe o código do cupom.")
        cupom = get_db().execute("SELECT * FROM cupom WHERE codigo = ?", (codigo,)).fetchone()
        if not cupom or not cupom["ativo"]:
            raise CupomInvalido("Cupom não encontrado.")
        validade = cupom["data_validade"]
        if isinstance(validade, str):
            validade = date.fromisoformat(validade)
        if validade < hoje:
            raise CupomInvalido("Este cupom expirou.")
        if cupom["quantidade_disponivel"] <= 0:
            raise CupomInvalido("Este cupom esgotou.")
        if valor_produtos < cupom["valor_minimo_pedido"]:
            raise CupomInvalido(
                f"Este cupom exige pedido mínimo de R$ {cupom['valor_minimo_pedido']:.2f}".replace(".", ",")
            )
        if cliente_id:  # cada cliente usa o cupom uma vez so (achado no laudo de teste)
            ja_usou = get_db().execute(
                "SELECT 1 FROM pedido WHERE cliente_id = ? AND cupom_id = ? AND status <> 'CANCELADO'",
                (cliente_id, cupom["id"])).fetchone()
            if ja_usou:
                raise CupomInvalido("Você já usou este cupom em outro pedido.")
        return cupom, Cupom.calcular_desconto(cupom["tipo_desconto"], cupom["valor_desconto"], valor_produtos)

    @staticmethod
    def listar():
        return get_db().execute("SELECT * FROM cupom ORDER BY ativo DESC, data_validade DESC").fetchall()

    @staticmethod
    def criar(dados: dict) -> int:
        db = get_db()
        cur = db.execute(
            "INSERT INTO cupom (codigo, tipo_desconto, valor_desconto, valor_minimo_pedido, data_validade, "
            "quantidade_disponivel) VALUES (?,?,?,?,?,?)",
            (dados["codigo"].strip().upper(), dados["tipo_desconto"],
             float(str(dados["valor_desconto"]).replace(",", ".")),
             float(str(dados.get("valor_minimo_pedido") or 0).replace(",", ".")),
             dados["data_validade"], int(dados["quantidade_disponivel"])),
        )
        db.commit()
        return cur.lastrowid

    @staticmethod
    def alternar_ativo(cupom_id):
        db = get_db()
        db.execute("UPDATE cupom SET ativo = 1 - ativo WHERE id = ?", (cupom_id,))
        db.commit()
