from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from ..models import EmailJaCadastrado, Usuario
from ..services.validacoes import validar_cadastro

bp = Blueprint("auth", __name__)


def _destino_seguro(proximo):
    return proximo if proximo and proximo.startswith("/") and not proximo.startswith("//") else None


def _pagina_inicial(usuario):
    if usuario["tipo"] == "ADMIN":
        return url_for("admin.painel")
    if usuario["tipo"] == "ENTREGADOR":
        return url_for("entregador.painel")
    return url_for("catalogo.inicio")


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if g.usuario:
        return redirect(url_for("catalogo.inicio"))
    dados = request.form
    if request.method == "POST":
        erros = validar_cadastro(dados.get("nome"), dados.get("email"), dados.get("telefone"),
                                 dados.get("senha"), dados.get("confirmacao"))
        if not dados.get("aceite_lgpd"):
            erros.append("É preciso aceitar os termos de uso e a política de privacidade (LGPD).")
        if not erros:
            try:
                uid = Usuario.criar(dados["nome"], dados["email"], dados["senha"], dados.get("telefone"))
                session.clear()
                session["usuario_id"] = uid
                flash("Conta criada com sucesso! Bem-vindo(a) à Sweet Dreams. 🧁", "sucesso")
                return redirect(_destino_seguro(request.args.get("proximo")) or url_for("catalogo.inicio"))
            except EmailJaCadastrado as e:
                erros.append(str(e))
        for erro in erros:
            flash(erro, "erro")
    return render_template("auth/cadastro.html", dados=dados)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.usuario:
        return redirect(_pagina_inicial(g.usuario))
    if request.method == "POST":
        usuario = Usuario.autenticar(request.form.get("email", ""), request.form.get("senha", ""))
        if usuario is None:
            flash("E-mail ou senha incorretos.", "erro")
            return render_template("auth/login.html", email=request.form.get("email", "")), 401
        carrinho = session.get("carrinho", {})  # preserva o carrinho do visitante
        session.clear()
        session["usuario_id"] = usuario["id"]
        session["carrinho"] = carrinho
        flash(f"Olá, {usuario['nome'].split()[0]}!", "sucesso")
        return redirect(_destino_seguro(request.args.get("proximo")) or _pagina_inicial(usuario))
    return render_template("auth/login.html", email="")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("catalogo.inicio"))
