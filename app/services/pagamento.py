"""Gateway de pagamento SIMULADO.

O projeto acadêmico não se integra a um gateway real. Este módulo reproduz
o comportamento de um gateway (validação, aprovação e recusa) para que o
fluxo completo do caso de uso CU-010 possa ser executado e testado.

Cartões de teste:
  * qualquer número válido pelo algoritmo de Luhn  -> APROVADO
  * número terminado em 0002 (ex.: 4000 0000 0000 0002) -> RECUSADO (saldo insuficiente)
"""
import secrets
from datetime import date

from .validacoes import somente_digitos


class PagamentoInvalido(ValueError):
    pass


def luhn_valido(numero: str) -> bool:
    digitos = somente_digitos(numero)
    if not 13 <= len(digitos) <= 19:
        return False
    soma = 0
    for i, d in enumerate(reversed(digitos)):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        soma += n
    return soma % 10 == 0


def identificar_bandeira(numero: str) -> str:
    d = somente_digitos(numero)
    if d.startswith("4"):
        return "Visa"
    if d[:2] in {"51", "52", "53", "54", "55"} or 2221 <= int(d[:4] or 0) <= 2720:
        return "Mastercard"
    if d[:2] in {"34", "37"}:
        return "Amex"
    if d.startswith(("636368", "438935", "504175", "451416", "636297", "5067", "4576", "4011")):
        return "Elo"
    return "Outra"


def validar_validade(mm_aa: str, hoje: date | None = None) -> bool:
    hoje = hoje or date.today()
    partes = (mm_aa or "").replace(" ", "").split("/")
    if len(partes) != 2 or not all(p.isdigit() for p in partes):
        return False
    mes, ano = int(partes[0]), int(partes[1])
    if not 1 <= mes <= 12:
        return False
    ano += 2000 if ano < 100 else 0
    return (ano, mes) >= (hoje.year, hoje.month)


def validar_dados_cartao(numero: str, nome: str, validade: str, cvv: str) -> list[str]:
    erros = []
    if not luhn_valido(numero):
        erros.append("Número do cartão inválido.")
    if not nome or len(nome.strip()) < 3:
        erros.append("Informe o nome impresso no cartão.")
    if not validar_validade(validade):
        erros.append("Validade inválida ou cartão vencido (use MM/AA).")
    if not (cvv or "").isdigit() or len(cvv) not in (3, 4):
        erros.append("CVV deve ter 3 ou 4 dígitos.")
    return erros


def processar_cartao(numero: str, nome: str, validade: str, cvv: str, valor: float) -> dict:
    """Simula a autorização. Retorna dict com status APROVADO ou RECUSADO."""
    erros = validar_dados_cartao(numero, nome, validade, cvv)
    if erros:
        raise PagamentoInvalido(" ".join(erros))
    if valor <= 0:
        raise PagamentoInvalido("Valor do pagamento deve ser maior que zero.")
    digitos = somente_digitos(numero)
    base = {"cartao_final": digitos[-4:], "bandeira": identificar_bandeira(digitos)}
    if digitos.endswith("0002"):
        return {**base, "status": "RECUSADO", "motivo": "Transação recusada pelo emissor (saldo insuficiente)."}
    return {**base, "status": "APROVADO", "codigo_transacao": "TX" + secrets.token_hex(6).upper()}


def gerar_pix(numero_pedido: str, valor: float) -> str:
    """Gera um código PIX 'copia e cola' fictício (formato ilustrativo)."""
    valor_txt = f"{valor:.2f}"
    return (
        "00020126580014BR.GOV.BCB.PIX0136sweetdreams@pix.com.br"
        f"52040000530398654{len(valor_txt):02d}{valor_txt}"
        f"5802BR5920SWEET DREAMS CUPCAKE6008CURITIBA62{len(numero_pedido) + 4:02d}05{len(numero_pedido):02d}{numero_pedido}6304"
        + secrets.token_hex(2).upper()
    )
