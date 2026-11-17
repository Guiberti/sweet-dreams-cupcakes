"""Cálculo de frete (regra de negócio RN-HU008).

Cupcakes são perecíveis, por isso a loja só entrega em Curitiba e Região
Metropolitana (CEPs 80000-000 a 83899-999). Fora dessa faixa, o cliente
pode escolher a retirada na loja.
"""
from .validacoes import somente_digitos

FRETE_GRATIS_A_PARTIR = 150.00
TABELA = [
    # (cep_inicial, cep_final, valor, prazo_em_minutos, descrição)
    (80000000, 81999999, 7.90, 60, "Curitiba"),
    (82000000, 83899999, 12.90, 90, "Região Metropolitana de Curitiba"),
]


class ForaDaAreaDeEntrega(ValueError):
    pass


def calcular_frete(cep: str, valor_produtos: float) -> dict:
    """Retorna {'valor', 'prazo_min', 'regiao'} ou lança ForaDaAreaDeEntrega."""
    digitos = somente_digitos(cep)
    if len(digitos) != 8:
        raise ValueError("CEP inválido: informe 8 dígitos.")
    numero = int(digitos)
    for inicio, fim, valor, prazo, regiao in TABELA:
        if inicio <= numero <= fim:
            if valor_produtos >= FRETE_GRATIS_A_PARTIR:
                valor = 0.0
            return {"valor": round(valor, 2), "prazo_min": prazo, "regiao": regiao}
    raise ForaDaAreaDeEntrega(
        "Ainda não entregamos neste CEP. Escolha 'Retirar na loja' para finalizar o pedido."
    )
