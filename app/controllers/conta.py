from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from ..models import Endereco, Usuario
from ..services.frete import ForaDaAreaDeEntrega, calcular_frete
from ..services.validacoes import validar_telefone
from .helpers import login_obrigatorio

bp = Blueprint("conta", __name__, url_prefix="/conta")


@bp.route("/", methods=["GET", "POST"])
@login_obrigatorio()
def perfil():
    if request.method == "POST":
        nome, tel = request.form.get("nome", ""), request.form.get("telefone", "")
        if len(nome.strip()) < 3:
            flash("Informe seu nome completo.", "erro")
        elif tel and not validar_telefone(tel):
            flash("Telefone deve ter DDD + número.", "erro")
        else:
            Usuario.atualizar_perfil(g.usuario["id"], nome, tel)
            flash("Dados atualizados.", "sucesso")
            return redirect(url_for("conta.perfil"))
    return render_template("conta/perfil.html", enderecos=Endereco.listar(g.usuario["id"]))


@bp.route("/enderecos/novo", methods=["GET", "POST"])
@login_obrigatorio()
def novo_endereco():
    dados = request.form
    if request.method == "POST":
        erros = Endereco.validar(dados)
        if not erros:
            novo_id = Endereco.criar(g.usuario["id"], dados)
            flash("Endereço salvo.", "sucesso")
            try:
                calcular_frete(dados.get("cep"), 0)
            except ForaDaAreaDeEntrega:
                flash("Atenção: ainda não entregamos neste CEP. Para ele, só a retirada na loja.", "aviso")
            if request.args.get("voltar") == "checkout":  # ja volta com o endereco novo marcado
                return redirect(url_for("pedidos.checkout", endereco_id=novo_id))
            return redirect(url_for("conta.perfil"))
        for e in erros:
            flash(e, "erro")
    return render_template("conta/endereco_form.html", dados=dados)


@bp.route("/enderecos/<int:endereco_id>/principal", methods=["POST"])
@login_obrigatorio()
def tornar_principal(endereco_id):
    Endereco.definir_principal(endereco_id, g.usuario["id"])
    return redirect(url_for("conta.perfil"))


@bp.route("/enderecos/<int:endereco_id>/excluir", methods=["POST"])
@login_obrigatorio()
def excluir_endereco(endereco_id):
    Endereco.excluir(endereco_id, g.usuario["id"])
    flash("Endereço excluído.", "info")
    return redirect(url_for("conta.perfil"))
