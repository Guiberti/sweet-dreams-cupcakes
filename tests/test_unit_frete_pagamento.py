# testes unitarios de frete e pagamento
from datetime import date

import pytest

from app.services.frete import ForaDaAreaDeEntrega, calcular_frete
from app.services.pagamento import (PagamentoInvalido, gerar_pix, identificar_bandeira, luhn_valido,
                                    processar_cartao, validar_validade)


# ------------------------------- Frete -------------------------------
def test_frete_curitiba():
    f = calcular_frete("80010-000", 50)
    assert f["valor"] == 7.90 and f["regiao"] == "Curitiba"


def test_frete_regiao_metropolitana():
    assert calcular_frete("83005000", 50)["valor"] == 12.90


def test_frete_gratis_acima_de_150():
    assert calcular_frete("80010000", 150.00)["valor"] == 0.0


def test_frete_fora_da_area():
    with pytest.raises(ForaDaAreaDeEntrega):
        calcular_frete("01310-100", 50)  # São Paulo


def test_frete_cep_invalido():
    with pytest.raises(ValueError):
        calcular_frete("123", 50)


# ------------------------------ Pagamento ------------------------------
@pytest.mark.parametrize("numero,esperado", [
    ("4111 1111 1111 1111", True), ("5555555555554444", True), ("4111111111111112", False), ("1234", False),
])
def test_luhn(numero, esperado):
    assert luhn_valido(numero) is esperado


def test_bandeiras():
    assert identificar_bandeira("4111111111111111") == "Visa"
    assert identificar_bandeira("5555555555554444") == "Mastercard"


@pytest.mark.parametrize("validade,esperado", [("12/30", True), ("01/20", False), ("13/30", False), ("1230", False)])
def test_validade_cartao(validade, esperado):
    assert validar_validade(validade, hoje=date(2026, 11, 17)) is esperado


def test_cartao_aprovado_guarda_somente_final():
    r = processar_cartao("4111 1111 1111 1111", "MARIA SOUZA", "12/30", "123", 50.0)
    assert r["status"] == "APROVADO" and r["cartao_final"] == "1111"
    assert r["codigo_transacao"].startswith("TX")
    assert "4111111111111111" not in str(r)


def test_cartao_recusado():
    r = processar_cartao("4000 0000 0000 0002", "MARIA SOUZA", "12/30", "123", 50.0)
    assert r["status"] == "RECUSADO" and "saldo" in r["motivo"]


def test_cartao_dados_invalidos():
    with pytest.raises(PagamentoInvalido) as e:
        processar_cartao("4111111111111112", "", "01/20", "1", 50.0)
    msg = str(e.value)
    assert "Número do cartão inválido" in msg and "CVV" in msg and "Validade" in msg


def test_pix_contem_valor_e_pedido():
    codigo = gerar_pix("SD000001", 42.5)
    assert "42.50" in codigo and "SD000001" in codigo and codigo.startswith("000201")
