from functools import wraps

from flask import abort, flash, g, redirect, request, session, url_for

from ..models import Produto, Usuario


def carregar_usuario():
    uid = session.get("usuario_id")
    g.usuario = Usuario.buscar_por_id(uid) if uid else None
    if g.usuario is not None and not g.usuario["ativo"]:
        session.clear()
        g.usuario = None


def login_obrigatorio(*tipos):
    # ex: @login_obrigatorio("ADMIN") -> so admin entra
    def decorador(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if g.usuario is None:
                flash("Faça login para continuar.", "aviso")
                return redirect(url_for("auth.login", proximo=request.full_path))
            if tipos and g.usuario["tipo"] not in tipos:
                abort(403)
            return view(*args, **kwargs)
        return wrapper
    return decorador


# ---------------------------- Carrinho (sessão) ----------------------------
def carrinho_bruto() -> dict:
    return session.setdefault("carrinho", {})


def itens_do_carrinho() -> list[dict]:
    itens = []
    for pid, qtd in carrinho_bruto().items():
        p = Produto.buscar(int(pid))
        if p and p["ativo"]:
            itens.append({"produto": p, "produto_id": p["id"], "quantidade": qtd, "preco": p["preco"],
                          "subtotal": round(p["preco"] * qtd, 2)})
    return itens


def contexto_global():
    qtd = sum(session.get("carrinho", {}).values())
    return {"usuario": g.get("usuario"), "qtd_carrinho": qtd}
