from flask import Blueprint, abort, render_template, request

from ..models import Categoria, Produto

bp = Blueprint("catalogo", __name__)


@bp.route("/")
def inicio():
    categoria_id = request.args.get("categoria", type=int)
    busca = (request.args.get("busca") or "").strip()[:60]
    produtos = Produto.listar(categoria_id=categoria_id, busca=busca or None)
    outra_categoria = None
    if busca and categoria_id and not produtos:
        # melhoria pedida no laudo: buscou "pistache" com o filtro Veganos ligado e achou que o produto nao existia
        produtos = Produto.listar(busca=busca)
        if produtos:
            outra_categoria = Categoria.buscar(categoria_id)
    return render_template("catalogo/inicio.html", produtos=produtos, categorias=Categoria.listar(),
                           categoria_atual=categoria_id, busca=busca, outra_categoria=outra_categoria)


@bp.route("/produto/<int:produto_id>")
def detalhe(produto_id):
    produto = Produto.buscar(produto_id)
    if not produto or not produto["ativo"]:
        abort(404)
    relacionados = [p for p in Produto.listar(categoria_id=produto["categoria_id"]) if p["id"] != produto_id][:3]
    return render_template("catalogo/detalhe.html", produto=produto, relacionados=relacionados)
