from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from ..models import Pedido, PedidoInvalido
from .helpers import login_obrigatorio

bp = Blueprint("entregador", __name__, url_prefix="/entregador")


@bp.route("/")
@login_obrigatorio("ENTREGADOR")
def painel():
    pedidos = Pedido.listar(entregador_id=g.usuario["id"])
    ativos = [p for p in pedidos if p["status"] not in ("ENTREGUE", "CANCELADO")]
    concluidos = [p for p in pedidos if p["status"] == "ENTREGUE"]
    return render_template("entregador/painel.html", ativos=ativos, concluidos=concluidos)


@bp.route("/pedido/<int:pedido_id>/status", methods=["POST"])
@login_obrigatorio("ENTREGADOR")
def atualizar(pedido_id):
    pedido = Pedido.buscar(pedido_id)
    if not pedido or pedido["entregador_id"] != g.usuario["id"]:
        abort(403)
    novo = request.form.get("status")
    if novo not in ("SAIU_PARA_ENTREGA", "ENTREGUE"):
        abort(400)
    try:
        Pedido.atualizar_status(pedido_id, novo, g.usuario["id"])
        flash("Entrega atualizada.", "sucesso")
    except PedidoInvalido as e:
        flash(str(e), "erro")
    return redirect(url_for("entregador.painel"))
