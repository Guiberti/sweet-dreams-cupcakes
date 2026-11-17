"""Testes UNITÁRIOS - totais, cupom e máquina de estados do pedido."""
from datetime import date

import pytest

from app.models import Cupom, CupomInvalido
from app.models.pedido import calcular_totais, transicao_permitida


def test_calcular_totais():
    itens = [{"preco": 12.90, "quantidade": 2}, {"preco": 14.90, "quantidade": 1}]
    t = calcular_totais(itens, frete=7.90, desconto=5.0)
    assert t == {"produtos": 40.70, "frete": 7.90, "desconto": 5.0, "total": 43.60}


def test_desconto_nunca_maior_que_produtos():
    t = calcular_totais([{"preco": 10.0, "quantidade": 1}], frete=0, desconto=50)
    assert t["desconto"] == 10.0 and t["total"] == 0.0


@pytest.mark.parametrize("tipo,valor,produtos,esperado", [
    ("PERCENTUAL", 10, 100.0, 10.0), ("VALOR_FIXO", 15, 100.0, 15.0), ("VALOR_FIXO", 15, 10.0, 10.0),
])
def test_calculo_desconto(tipo, valor, produtos, esperado):
    assert Cupom.calcular_desconto(tipo, valor, produtos) == esperado


@pytest.mark.parametrize("atual,novo,tipo,esperado", [
    ("AGUARDANDO_PAGAMENTO", "CONFIRMADO", "ENTREGA", True),
    ("AGUARDANDO_PAGAMENTO", "ENTREGUE", "ENTREGA", False),
    ("CONFIRMADO", "EM_PREPARO", "ENTREGA", True),
    ("EM_PREPARO", "SAIU_PARA_ENTREGA", "ENTREGA", True),
    ("EM_PREPARO", "ENTREGUE", "ENTREGA", False),      # entrega precisa sair para entrega
    ("EM_PREPARO", "ENTREGUE", "RETIRADA", True),      # retirada vai direto
    ("EM_PREPARO", "SAIU_PARA_ENTREGA", "RETIRADA", False),
    ("ENTREGUE", "CANCELADO", "ENTREGA", False),
    ("SAIU_PARA_ENTREGA", "CANCELADO", "ENTREGA", False),
])
def test_maquina_de_estados(atual, novo, tipo, esperado):
    assert transicao_permitida(atual, novo, tipo) is esperado


# Cupom.validar consulta o banco: usa o fixture ctx (banco de teste com dados demo)
def test_cupom_valido(ctx):
    cupom, desconto = Cupom.validar("bemvindo10", 50.0, hoje=date(2026, 11, 17))
    assert cupom["codigo"] == "BEMVINDO10" and desconto == 5.0


@pytest.mark.parametrize("codigo,valor,mensagem", [
    ("EXPIRADO", 50.0, "expirou"), ("NAOEXISTE", 50.0, "não encontrado"),
    ("DOCE15", 30.0, "pedido mínimo"), ("", 30.0, "Informe"),
])
def test_cupom_invalido(ctx, codigo, valor, mensagem):
    with pytest.raises(CupomInvalido, match=mensagem):
        Cupom.validar(codigo, valor, hoje=date(2026, 11, 17))
