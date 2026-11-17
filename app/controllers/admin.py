"""Controller do administrador: HU-018 (produtos), HU-019 (pedidos), HU-020 (relatórios),
HU-021 (cupons), HU-022 (atribuir entregador) e laudos de teste."""
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from ..models import (STATUS_ROTULOS, Categoria, Cupom, FeedbackTeste, Pagamento, Pedido, PedidoInvalido,
                      Produto, Usuario)
from .helpers import login_obrigatorio

bp = Blueprint("admin", __name__, url_prefix="/admin")
ORDEM = ["CONFIRMADO", "EM_PREPARO", "SAIU_PARA_ENTREGA", "ENTREGUE", "CANCELADO"]


@bp.route("/")
@login_obrigatorio("ADMIN")
def painel():
    return render_template("admin/painel.html", resumo=Pedido.resumo_vendas(),
                           pendentes=Pedido.listar(status="CONFIRMADO"))


# ------------------------------ Produtos ------------------------------
@bp.route("/produtos")
@login_obrigatorio("ADMIN")
def produtos():
    return render_template("admin/produtos.html", produtos=Produto.listar(somente_ativos=False))


@bp.route("/produtos/novo", methods=["GET", "POST"])
@bp.route("/produtos/<int:produto_id>/editar", methods=["GET", "POST"])
@login_obrigatorio("ADMIN")
def produto_form(produto_id=None):
    produto = Produto.buscar(produto_id) if produto_id else None
    if produto_id and not produto:
        abort(404)
    if request.method == "POST":
        erros = Produto.validar(request.form)
        if not erros:
            if produto:
                Produto.atualizar(produto_id, request.form)
                flash("Produto atualizado.", "sucesso")
            else:
                Produto.criar(request.form)
                flash("Produto cadastrado.", "sucesso")
            return redirect(url_for("admin.produtos"))
        for e in erros:
            flash(e, "erro")
    return render_template("admin/produto_form.html", produto=produto, dados=request.form or produto,
                           categorias=Categoria.listar())


@bp.route("/produtos/<int:produto_id>/desativar", methods=["POST"])
@login_obrigatorio("ADMIN")
def produto_desativar(produto_id):
    Produto.desativar(produto_id)
    flash("Produto desativado (continua no histórico de pedidos).", "info")
    return redirect(url_for("admin.produtos"))


# ------------------------------ Pedidos ------------------------------
@bp.route("/pedidos")
@login_obrigatorio("ADMIN")
def pedidos():
    status = request.args.get("status") or None
    return render_template("admin/pedidos.html", pedidos=Pedido.listar(status=status), status_atual=status,
                           rotulos=STATUS_ROTULOS)


@bp.route("/pedidos/<int:pedido_id>", methods=["GET", "POST"])
@login_obrigatorio("ADMIN")
def pedido(pedido_id):
    p = Pedido.buscar(pedido_id)
    if not p:
        abort(404)
    if request.method == "POST":
        try:
            if request.form.get("acao") == "status":
                Pedido.atualizar_status(pedido_id, request.form.get("status"), g.usuario["id"])
                flash("Status atualizado.", "sucesso")
            elif request.form.get("acao") == "entregador":
                Pedido.atribuir_entregador(pedido_id, request.form.get("entregador_id", type=int))
                flash("Entregador atribuído.", "sucesso")
        except PedidoInvalido as e:
            flash(str(e), "erro")
        return redirect(url_for("admin.pedido", pedido_id=pedido_id))
    from ..models.pedido import TRANSICOES, transicao_permitida
    proximos = [s for s in TRANSICOES[p["status"]] if transicao_permitida(p["status"], s, p["tipo_entrega"])]
    return render_template("admin/pedido.html", pedido=p, itens=Pedido.itens(pedido_id),
                           historico=Pedido.historico(pedido_id), pagamento=Pagamento.ultimo(pedido_id),
                           proximos=sorted(proximos, key=ORDEM.index), rotulos=STATUS_ROTULOS,
                           entregadores=Usuario.listar_por_tipo("ENTREGADOR"))


# ------------------------------ Cupons ------------------------------
@bp.route("/cupons", methods=["GET", "POST"])
@login_obrigatorio("ADMIN")
def cupons():
    if request.method == "POST":
        f = request.form
        erros = []
        if len((f.get("codigo") or "").strip()) < 3:
            erros.append("Código deve ter pelo menos 3 caracteres.")
        try:
            v = float((f.get("valor_desconto") or "0").replace(",", "."))
            if v <= 0 or (f.get("tipo_desconto") == "PERCENTUAL" and v > 100):
                erros.append("Desconto inválido (percentual entre 1 e 100).")
            int(f.get("quantidade_disponivel") or "x")
        except ValueError:
            erros.append("Preencha valor e quantidade com números.")
        if not f.get("data_validade"):
            erros.append("Informe a validade.")
        if not erros:
            try:
                Cupom.criar(f)
                flash("Cupom criado.", "sucesso")
                return redirect(url_for("admin.cupons"))
            except Exception:
                erros.append("Já existe um cupom com esse código.")
        for e in erros:
            flash(e, "erro")
    return render_template("admin/cupons.html", cupons=Cupom.listar())


@bp.route("/cupons/<int:cupom_id>/alternar", methods=["POST"])
@login_obrigatorio("ADMIN")
def cupom_alternar(cupom_id):
    Cupom.alternar_ativo(cupom_id)
    return redirect(url_for("admin.cupons"))


@bp.route("/laudos")
@login_obrigatorio("ADMIN")
def laudos():
    return render_template("admin/laudos.html", laudos=FeedbackTeste.listar())
