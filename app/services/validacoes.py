import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def somente_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def validar_email(email: str) -> bool:
    return bool(email) and len(email) <= 160 and bool(EMAIL_RE.match(email.strip()))


def validar_senha(senha: str) -> list[str]:
    erros = []
    senha = senha or ""
    if len(senha) < 8:
        erros.append("A senha deve ter no mínimo 8 caracteres.")
    if not re.search(r"[A-Za-z]", senha):
        erros.append("A senha deve conter pelo menos uma letra.")
    if not re.search(r"\d", senha):
        erros.append("A senha deve conter pelo menos um número.")
    return erros


def validar_telefone(telefone: str) -> bool:
    digitos = somente_digitos(telefone)
    return len(digitos) in (10, 11)


def validar_cep(cep: str) -> bool:
    return len(somente_digitos(cep)) == 8


def validar_cadastro(nome: str, email: str, telefone: str, senha: str, confirmacao: str) -> list[str]:
    erros = []
    if not nome or len(nome.strip()) < 3:
        erros.append("Informe seu nome completo (mínimo 3 letras).")
    if not validar_email(email):
        erros.append("Informe um e-mail válido.")
    if telefone and not validar_telefone(telefone):
        erros.append("Telefone deve ter DDD + número (10 ou 11 dígitos).")
    erros.extend(validar_senha(senha))
    if senha != confirmacao:
        erros.append("A confirmação de senha não confere.")
    return erros
