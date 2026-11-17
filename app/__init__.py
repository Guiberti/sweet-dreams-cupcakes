# cria o app flask, registra os blueprints e os filtros dos templates
import os
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template

from . import db


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-sweet-dreams-troque-em-producao"),
        DATABASE=str(Path(app.instance_path) / "sweetdreams.sqlite"),
        UPLOAD_FOLDER=str(Path(app.root_path) / "static" / "uploads"),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # prints de até 5 MB
    )
    if config:
        app.config.update(config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    # Cria o banco automaticamente na primeira execução
    if not app.config.get("TESTING") and not Path(app.config["DATABASE"]).exists():
        with app.app_context():
            db.init_db()

    from .controllers import admin, auth, carrinho, catalogo, conta, entregador, feedback, pedidos
    for bp in (auth.bp, catalogo.bp, carrinho.bp, pedidos.bp, conta.bp, admin.bp, entregador.bp, feedback.bp):
        app.register_blueprint(bp)

    from .controllers.helpers import carregar_usuario, contexto_global
    app.before_request(carregar_usuario)
    app.context_processor(contexto_global)

    @app.template_filter("moeda")
    def moeda(valor):
        valor = float(valor or 0)
        return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @app.template_filter("data")
    def data(valor, formato="%d/%m/%Y %H:%M"):
        if not valor:
            return ""
        if isinstance(valor, str):
            tem_hora = len(valor) > 10
            try:
                valor = datetime.fromisoformat(valor)
            except ValueError:
                return valor
            if tem_hora:  # o sqlite grava CURRENT_TIMESTAMP em UTC, aqui converte pro horario de Brasilia
                valor = valor - timedelta(hours=3)
        return valor.strftime(formato)

    @app.errorhandler(404)
    def nao_encontrado(_e):
        return render_template("erros/erro.html", codigo=404,
                               mensagem="A página que você procurou não existe."), 404

    @app.errorhandler(403)
    def proibido(_e):
        return render_template("erros/erro.html", codigo=403,
                               mensagem="Você não tem permissão para acessar esta área."), 403

    @app.errorhandler(413)
    def grande_demais(_e):
        return render_template("erros/erro.html", codigo=413,
                               mensagem="Arquivo muito grande. Envie imagens de até 5 MB."), 413

    @app.errorhandler(500)
    def erro_interno(_e):
        return render_template("erros/erro.html", codigo=500,
                               mensagem="Algo deu errado do nosso lado. Tente novamente em instantes."), 500

    return app
