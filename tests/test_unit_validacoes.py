# testes unitarios das validacoes do cadastro
import pytest

from app.services.validacoes import (validar_cadastro, validar_cep, validar_email, validar_senha,
                                     validar_telefone)


@pytest.mark.parametrize("email,esperado", [
    ("maria@gmail.com", True), ("joao.silva+doces@empresa.com.br", True),
    ("sem-arroba.com", False), ("a@b", False), ("", False), ("maria @gmail.com", False),
])
def test_validar_email(email, esperado):
    assert validar_email(email) is esperado


def test_senha_valida_nao_gera_erros():
    assert validar_senha("Doce1234") == []


@pytest.mark.parametrize("senha,trecho", [
    ("Ab1", "mínimo 8"), ("somenteletras", "número"), ("12345678", "letra"),
])
def test_senha_invalida(senha, trecho):
    assert any(trecho in e for e in validar_senha(senha))


@pytest.mark.parametrize("tel,esperado", [("(41) 99999-0000", True), ("4133334444", True), ("9999", False)])
def test_validar_telefone(tel, esperado):
    assert validar_telefone(tel) is esperado


def test_validar_cep():
    assert validar_cep("80010-000") and not validar_cep("8001")


def test_cadastro_confirmacao_diferente():
    erros = validar_cadastro("Maria Souza", "maria@gmail.com", "", "Doce1234", "Doce9999")
    assert "A confirmação de senha não confere." in erros


def test_cadastro_completo_valido():
    assert validar_cadastro("Maria Souza", "maria@gmail.com", "41999990000", "Doce1234", "Doce1234") == []
