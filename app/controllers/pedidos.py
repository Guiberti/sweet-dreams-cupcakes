from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

from ..models import Cupom, CupomInvalido, Endereco, Pagamento, Pedido, PedidoInvalido
from ..models.pedido import calcular_totais
from ..services.frete import ForaDaAreaDeEntrega, calcular_frete
from ..services.pagamento import PagamentoInvalido, gerar_pix, processar_cartao
from .helpers import itens_do_carrinho, login_obrigatorio

bp = Blueprint("pedidos", __name__)
ETAPAS = ["AGUARDANDO_PAGAMENTO", "CONFIRMADO", "EM_PREPARO", "SAIU_PARA_ENTREGA", "ENTREGUE"]


def _pedido_do_cliente(pedido_id):
    pedido = Pedido.buscar(pedido_id)
    if not pedido:
        abort(404)
    if pedido["cliente_id"] != g.usuario["id"] and g.usuario["tipo"] != "ADMIN":
        abort(403)
    return pedido


@bp.route("/checkout", methods=["GET", "POST"])
@login_obrigatorio("CLIENTE", "ADMIN")
def checkout():
    itens = itens_do_carrinho()
    if not itens:
        flash("Seu carrinho está vazio.", "aviso")
        return redirect(url_for("catalogo.inicio"))
    enderecos = Endereco.listar(g.usuario["id"])
    form = request.form if request.method == "POST" else request.args
    tipo = form.get("tipo_entrega", "ENTREGA")
    endereco_id = form.get("endereco_id", type=int) or (enderecos[0]["id"] if enderecos else None)
    endereco = Endereco.buscar(endereco_id, g.usuario["id"]) if endereco_id else None

    produtos = calcular_totais(itens)["produtos"]
    desconto, cupom_codigo = 0.0, session.get("cupom")
    if cupom_codigo:
        try:
            _, desconto = Cupom.validar(cupom_codigo, produtos)
        except CupomInvalido:
            cupom_codigo = None
            session.pop("cupom", None)

    frete_info, erro_frete = None, None
    if tipo == "ENTREGA" and endereco:
        try:
            frete_info = calcular_frete(endereco["cep"], produtos)
        except (ForaDaAreaDeEntrega, ValueError) as e:
            erro_frete = str(e)
    frete = frete_info["valor"] if frete_info else 0.0
    totais = calcular_totais(itens, frete, desconto)

    if request.method == "POST":
        if tipo == "ENTREGA" and not endereco:
            flash("Cadastre ou selecione um endereço de entrega.", "erro")
        elif tipo == "ENTREGA" and erro_frete:
            flash(erro_frete, "erro")
        else:
            try:
                pedido_id = Pedido.criar(
                    g.usuario["id"], [{"produto_id": i["produto_id"], "quantidade": i["quantidade"]} for i in itens],
                    tipo, Endereco.formatar(endereco) if tipo == "ENTREGA" else None, frete, cupom_codigo,
                    request.form.get("observacoes"))
                session.pop("carrinho", None)
                session.pop("cupom", None)
                return redirect(url_for("pedidos.pagamento", pedido_id=pedido_id))
            except (PedidoInvalido, CupomInvalido) as e:
                flash(str(e), "erro")
    return render_template("pedidos/checkout.html", itens=itens, enderecos=enderecos, endereco=endereco,
                           tipo=tipo, frete_info=frete_info, erro_frete=erro_frete, totais=totais,
                           cupom_codigo=cupom_codigo)


@bp.route("/pedido/<int:pedido_id>/pagamento", methods=["GET", "POST"])
@login_obrigatorio()
def pagamento(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    if pedido["status"] != "AGUARDANDO_PAGAMENTO":
        return redirect(url_for("pedidos.acompanhar", pedido_id=pedido_id))
    pix = Pagamento.ultimo(pedido_id)
    pix = pix if pix and pix["forma"] == "PIX" and pix["status"] == "PENDENTE" else None

    if request.method == "POST":
        forma = request.form.get("forma")
        if forma == "CARTAO":
            try:
                r = processar_cartao(request.form.get("numero", ""), request.form.get("nome_cartao", ""),
                                     request.form.get("validade", ""), request.form.get("cvv", ""),
                                     pedido["valor_total"])
                extras = {k: v for k, v in r.items() if k != "status"}
                Pagamento.registrar(pedido_id, "CARTAO", r["status"], pedido["valor_total"], **extras)
                if r["status"] == "APROVADO":
                    Pedido.atualizar_status(pedido_id, "CONFIRMADO", g.usuario["id"])
                    flash("Pagamento aprovado! Seu pedido foi confirmado. 🎉", "sucesso")
                    return redirect(url_for("pedidos.acompanhar", pedido_id=pedido_id))
                flash(f"Pagamento recusado: {r['motivo']} Tente outro cartão ou pague com PIX.", "erro")
            except PagamentoInvalido as e:
                flash(str(e), "erro")
        elif forma == "PIX":
            codigo = gerar_pix(pedido["numero"], pedido["valor_total"])
            Pagamento.registrar(pedido_id, "PIX", "PENDENTE", pedido["valor_total"], pix_copia_cola=codigo)
            return redirect(url_for("pedidos.pagamento", pedido_id=pedido_id))
        else:
            flash("Escolha uma forma de pagamento.", "erro")
    return render_template("pedidos/pagamento.html", pedido=pedido, pix=pix)


@bp.route("/pedido/<int:pedido_id>/pix/confirmar", methods=["POST"])
@login_obrigatorio()
def confirmar_pix(pedido_id):
    # simula o aviso do banco de que o pix caiu (so pra demonstracao)
    pedido = _pedido_do_cliente(pedido_id)
    pix = Pagamento.ultimo(pedido_id)
    if pedido["status"] == "AGUARDANDO_PAGAMENTO" and pix and pix["forma"] == "PIX" and pix["status"] == "PENDENTE":
        Pagamento.aprovar_pix(pix["id"])
        Pedido.atualizar_status(pedido_id, "CONFIRMADO", g.usuario["id"])
        flash("PIX recebido! Seu pedido foi confirmado. 🎉", "sucesso")
    return redirect(url_for("pedidos.acompanhar", pedido_id=pedido_id))


@bp.route("/pedido/<int:pedido_id>")
@login_obrigatorio()
def acompanhar(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    etapas = [e for e in ETAPAS if not (pedido["tipo_entrega"] == "RETIRADA" and e == "SAIU_PARA_ENTREGA")]
    return render_template("pedidos/acompanhar.html", pedido=pedido, itens=Pedido.itens(pedido_id),
                           historico=Pedido.historico(pedido_id), pagamento=Pagamento.ultimo(pedido_id),
                           etapas=etapas)


@bp.route("/pedido/<int:pedido_id>/cancelar", methods=["POST"])
@login_obrigatorio()
def cancelar(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    if pedido["status"] not in ("AGUARDANDO_PAGAMENTO", "CONFIRMADO"):
        flash("Este pedido já está em preparo e não pode mais ser cancelado pelo app.", "erro")
    else:
        Pedido.atualizar_status(pedido_id, "CANCELADO", g.usuario["id"])
        flash("Pedido cancelado.", "info")
    return redirect(url_for("pedidos.acompanhar", pedido_id=pedido_id))


@bp.route("/meus-pedidos")
@login_obrigatorio()
def meus_pedidos():
    return render_template("pedidos/meus_pedidos.html", pedidos=Pedido.listar_do_cliente(g.usuario["id"]))
