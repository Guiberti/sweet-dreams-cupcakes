"""Controller do formulário de laudo de teste (Situação-Problema 3).

Os 5 testadores acessam /teste, descrevem o que funcionou, o que não
funcionou, o que não testaram e anexam um print. O administrador consulta
todos os laudos em /admin/laudos.
"""
import secrets
from datetime import date
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from ..models import FeedbackTeste

bp = Blueprint("feedback", __name__, url_prefix="/teste")
EXTENSOES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


@bp.route("/", methods=["GET", "POST"])
def formulario():
    dados = request.form
    if request.method == "POST":
        erros = FeedbackTeste.validar(dados)
        arquivo = request.files.get("print")
        nome_arquivo = None
        if arquivo and arquivo.filename:
            ext = Path(arquivo.filename).suffix.lower()
            if ext not in EXTENSOES:
                erros.append("O print deve ser uma imagem (PNG, JPG, WEBP ou GIF).")
            else:
                nome_arquivo = f"laudo_{secrets.token_hex(6)}{ext}"
        if not erros:
            if nome_arquivo:
                arquivo.save(Path(current_app.config["UPLOAD_FOLDER"]) / nome_arquivo)
            FeedbackTeste.criar(dados, nome_arquivo)
            return redirect(url_for("feedback.obrigado"))
        for e in erros:
            flash(e, "erro")
    return render_template("feedback/formulario.html", dados=dados, hoje=date.today().isoformat())


@bp.route("/obrigado")
def obrigado():
    return render_template("feedback/obrigado.html")
