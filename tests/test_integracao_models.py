# testes de integracao (model + banco)
import pytest

from app.db import get_db
from app.models import EmailJaCadastrado, Pedido, PedidoInvalido, Produto, Usuario


def estoque(pid):
    return Produto.buscar(pid)["estoque"]


def test_usuario_senha_guardada_com_hash(ctx):
    uid = Usuario.criar("Ana Lima", "ANA@Teste.com", "Doce1234")
    u = Usuario.buscar_por_id(uid)
    assert u["email"] == "ana@teste.com" and u["senha_hash"] != "Doce1234"
    assert Usuario.autenticar("ana@teste.com", "Doce1234")["id"] == uid
    assert Usuario.autenticar("ana@teste.com", "errada123") is None


def test_email_duplicado(ctx):
    with pytest.raises(EmailJaCadastrado):
        Usuario.criar("Outro", "cliente@teste.com", "Doce1234")


def test_criar_pedido_baixa_estoque_e_calcula_total(ctx):
    antes = estoque(1)
    pid = Pedido.criar(3, [{"produto_id": 1, "quantidade": 2}], "ENTREGA", "Rua X, 1", 7.90, "BEMVINDO10")
    p = Pedido.buscar(pid)
    assert p["numero"] == f"SD{pid:06d}" and p["status"] == "AGUARDANDO_PAGAMENTO"
    assert p["valor_produtos"] == 25.80 and p["valor_desconto"] == 2.58 and p["valor_total"] == 31.12
    assert estoque(1) == antes - 2
    assert len(Pedido.historico(pid)) == 1


def test_estoque_insuficiente_faz_rollback(ctx):
    antes1, antes8 = estoque(1), estoque(8)  # produto 8 (Nutella) está com estoque 0
    with pytest.raises(PedidoInvalido, match="Estoque insuficiente"):
        Pedido.criar(3, [{"produto_id": 1, "quantidade": 1}, {"produto_id": 8, "quantidade": 1}], "RETIRADA", None, 0)
    assert estoque(1) == antes1 and estoque(8) == antes8
    assert get_db().execute("SELECT COUNT(*) FROM pedido").fetchone()[0] == 0


def test_retirada_zera_frete(ctx):
    pid = Pedido.criar(3, [{"produto_id": 2, "quantidade": 1}], "RETIRADA", None, 99.0)
    assert Pedido.buscar(pid)["valor_frete"] == 0


def test_entrega_exige_endereco(ctx):
    with pytest.raises(PedidoInvalido, match="endereço"):
        Pedido.criar(3, [{"produto_id": 2, "quantidade": 1}], "ENTREGA", None, 7.9)


def test_cancelamento_devolve_estoque(ctx):
    antes = estoque(3)
    pid = Pedido.criar(3, [{"produto_id": 3, "quantidade": 4}], "RETIRADA", None, 0)
    Pedido.atualizar_status(pid, "CANCELADO", 3)
    assert estoque(3) == antes


def test_transicao_invalida_e_bloqueada(ctx):
    pid = Pedido.criar(3, [{"produto_id": 2, "quantidade": 1}], "ENTREGA", "Rua X, 1", 7.9)
    with pytest.raises(PedidoInvalido, match="Não é possível"):
        Pedido.atualizar_status(pid, "ENTREGUE")


def test_cupom_decrementa_quantidade(ctx):
    db = get_db()
    antes = db.execute("SELECT quantidade_disponivel FROM cupom WHERE codigo='BEMVINDO10'").fetchone()[0]
    Pedido.criar(3, [{"produto_id": 2, "quantidade": 1}], "RETIRADA", None, 0, "BEMVINDO10")
    depois = db.execute("SELECT quantidade_disponivel FROM cupom WHERE codigo='BEMVINDO10'").fetchone()[0]
    assert depois == antes - 1


def test_entregador_so_em_pedido_pago(ctx):
    pid = Pedido.criar(3, [{"produto_id": 2, "quantidade": 1}], "ENTREGA", "Rua X, 1", 7.9)
    with pytest.raises(PedidoInvalido, match="pago"):
        Pedido.atribuir_entregador(pid, 2)
    Pedido.atualizar_status(pid, "CONFIRMADO")
    Pedido.atribuir_entregador(pid, 2)
    assert Pedido.buscar(pid)["entregador_id"] == 2
