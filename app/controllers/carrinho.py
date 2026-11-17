# o carrinho fica guardado na sessao (funciona sem login)
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from ..models import Cupom, CupomInvalido, Produto
from ..models.pedido import calcular_totais
from .helpers import carrinho_bruto, itens_do_carrinho

bp = Blueprint("carrinho", __name__, url_prefix="/carrinho")
MAX_POR_ITEM = 50


def _cliente_id():
    return g.usuario["id"] if g.get("usuario") else None


def _resumo():
    itens = itens_do_carrinho()
    desconto, cupom = 0.0, None
    codigo = session.get("cupom")
    if codigo and itens:
        try:
            cupom, desconto = Cupom.validar(codigo, calcular_totais(itens)["produtos"], cliente_id=_cliente_id())
        except CupomInvalido as e:
            session.pop("cupom", None)
            flash(f"Cupom removido: {e}", "aviso")
    return itens, cupom, calcular_totais(itens, 0.0, desconto)


@bp.route("/")
def ver():
    itens, cupom, totais = _resumo()
    return render_template("carrinho/carrinho.html", itens=itens, cupom=cupom, totais=totais)


@bp.route("/adicionar/<int:produto_id>", methods=["POST"])
def adicionar(produto_id):
    produto = Produto.buscar(produto_id)
    if not produto or not produto["ativo"]:
        flash("Produto indisponível.", "erro")
        return redirect(url_for("catalogo.inicio"))
    qtd = max(1, request.form.get("quantidade", 1, type=int) or 1)
    carrinho = carrinho_bruto()
    nova = carrinho.get(str(produto_id), 0) + qtd
    if nova > produto["estoque"]:
        flash(f"Só temos {produto['estoque']} unidade(s) de {produto['nome']} no momento.", "erro")
        return redirect(request.referrer or url_for("catalogo.inicio"))
    carrinho[str(produto_id)] = min(nova, MAX_POR_ITEM)
    session.modified = True
    flash(f"{produto['nome']} adicionado ao carrinho! 🧁", "sucesso")
    return redirect(request.referrer or url_for("catalogo.inicio"))


@bp.route("/atualizar/<int:produto_id>", methods=["POST"])
def atualizar(produto_id):
    carrinho = carrinho_bruto()
    qtd = request.form.get("quantidade", type=int)
    produto = Produto.buscar(produto_id)
    if qtd is None or produto is None:
        flash("Quantidade inválida.", "erro")
    elif qtd <= 0:
        carrinho.pop(str(produto_id), None)
        flash(f"{produto['nome']} removido do carrinho.", "info")
    elif qtd > produto["estoque"]:
        flash(f"Só temos {produto['estoque']} unidade(s) de {produto['nome']}.", "erro")
    else:
        carrinho[str(produto_id)] = min(qtd, MAX_POR_ITEM)
    session.modified = True
    return redirect(url_for("carrinho.ver"))


@bp.route("/remover/<int:produto_id>", methods=["POST"])
def remover(produto_id):
    carrinho_bruto().pop(str(produto_id), None)
    session.modified = True
    flash("Item removido do carrinho.", "info")
    return redirect(url_for("carrinho.ver"))


@bp.route("/cupom", methods=["POST"])
def aplicar_cupom():
    codigo = (request.form.get("codigo") or "").strip().upper()
    itens = itens_do_carrinho()
    if not itens:
        flash("Adicione produtos antes de aplicar um cupom.", "aviso")
        return redirect(url_for("carrinho.ver"))
    try:
        cupom, desconto = Cupom.validar(codigo, calcular_totais(itens)["produtos"], cliente_id=_cliente_id())
        session["cupom"] = cupom["codigo"]
        flash(f"Cupom {cupom['codigo']} aplicado: desconto de R$ {desconto:.2f}".replace(".", ","), "sucesso")
    except CupomInvalido as e:
        flash(str(e), "erro")
    return redirect(url_for("carrinho.ver"))


@bp.route("/cupom/remover", methods=["POST"])
def remover_cupom():
    session.pop("cupom", None)
    flash("Cupom removido. O desconto saiu do pedido.", "info")
    return redirect(url_for("carrinho.ver"))
