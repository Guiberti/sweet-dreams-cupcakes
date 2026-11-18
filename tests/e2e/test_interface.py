# testes de interface (ponta a ponta) num navegador de verdade (chromium via playwright)
# para rodar:  pip install playwright  &&  playwright install chromium
#              python -m pytest tests/e2e -v
# os prints de cada teste ficam em docs/situacao-3-testes-validacao/e2e/
import re
import threading
from pathlib import Path

import pytest

pw = pytest.importorskip("playwright.sync_api")

from werkzeug.serving import make_server  # noqa: E402

from app import create_app  # noqa: E402
from app.db import init_db  # noqa: E402

PRINTS = Path(__file__).resolve().parents[2] / "docs" / "situacao-3-testes-validacao" / "e2e"
CELULAR = {"width": 390, "height": 844}


@pytest.fixture(scope="module")
def servidor(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("e2e")
    app = create_app({"TESTING": True, "DATABASE": str(pasta / "e2e.sqlite"), "UPLOAD_FOLDER": str(pasta),
                      "SECRET_KEY": "e2e"})
    with app.app_context():
        init_db()
    srv = make_server("127.0.0.1", 0, app, threaded=True)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


@pytest.fixture(scope="module")
def navegador():
    with pw.sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def page(navegador, servidor, request):
    ctx = navegador.new_context(viewport=CELULAR, is_mobile=True, locale="pt-BR", base_url=servidor)
    pg = ctx.new_page()
    erros_js = []
    pg.on("pageerror", lambda e: erros_js.append(str(e)))
    yield pg
    PRINTS.mkdir(parents=True, exist_ok=True)
    nome = re.sub(r"[^\w-]+", "_", request.node.name).strip("_")
    pg.screenshot(path=str(PRINTS / f"{nome}.png"), full_page=False)
    ctx.close()
    assert not erros_js, f"erro de JavaScript na página: {erros_js}"


def ver(page, texto):
    # espera o texto aparecer (a pagina pode ainda estar carregando depois do clique)
    page.get_by_text(texto).first.wait_for(timeout=5000)


def entrar(page, email="cliente@teste.com", senha="Cliente@123"):
    page.goto("/login")
    page.fill("#email", email)
    page.fill("#senha", senha)
    page.click("form.formulario button.btn-primario")


def preencher_cartao(page, numero):
    page.fill("#numero", "")
    page.type("#numero", numero)
    page.fill("#nome_cartao", "CLIENTE TESTE")
    page.fill("#validade", "")
    page.type("#validade", "1230")
    page.fill("#cvv", "123")


# ------------------------------------------------------------------ fluxo principal
def test_compra_completa_pela_interface(page):
    page.goto("/")
    page.locator(".card-produto", has_text="Red Velvet").locator(".btn-mais").click()
    assert page.locator("[data-testid=contador-carrinho]").inner_text() == "1"
    page.goto("/carrinho/")
    page.fill("#codigo", "bemvindo10")
    page.click("text=Aplicar")
    ver(page, "Cupom BEMVINDO10 aplicado")
    page.click("text=Finalizar pedido")
    assert "/login" in page.url  # visitante precisa entrar
    page.fill("#email", "cliente@teste.com")
    page.fill("#senha", "Cliente@123")
    page.click("form.formulario button.btn-primario")
    assert "/checkout" in page.url
    assert "R$ 19,51" in page.inner_text("[data-testid=total-checkout]")  # 12,90 - 10% + 7,90
    page.click("text=Ir para o pagamento")
    preencher_cartao(page, "4111111111111111")
    page.click("text=Pagar")
    ver(page, "Pagamento aprovado")
    assert page.locator(".linha-tempo li.atual").inner_text().startswith("Pagamento confirmado")


def test_pagamento_recusado_e_depois_pix(page):
    entrar(page)
    page.goto("/produto/2")
    page.click("text=Adicionar ao carrinho")
    page.goto("/checkout?tipo_entrega=RETIRADA")
    page.click("text=Ir para o pagamento")
    preencher_cartao(page, "4000000000000002")
    page.click("text=Pagar")
    ver(page, "Pagamento recusado")
    page.click("text=⚡ PIX")
    page.click("text=Gerar código PIX")
    assert page.input_value("#pix-codigo").startswith("000201")
    page.click("text=Simular pagamento PIX recebido")
    ver(page, "PIX recebido")


# ------------------------------------------------------------------ javascript da tela
def test_mascaras_de_entrada(page):
    entrar(page)
    page.goto("/produto/3")
    page.click("text=Adicionar ao carrinho")
    page.goto("/checkout?tipo_entrega=RETIRADA")
    page.click("text=Ir para o pagamento")
    page.type("#numero", "4111111111111111")
    page.type("#validade", "1230")
    assert page.input_value("#numero") == "4111 1111 1111 1111"
    assert page.input_value("#validade") == "12/30"
    page.goto("/conta/enderecos/novo")
    page.type("#cep", "80010000")
    assert page.input_value("#cep") == "80010-000"
    page.goto("/conta/")
    page.fill("#telefone", "")
    page.type("#telefone", "41999998888")
    assert page.input_value("#telefone") == "(41) 99999-8888"


def test_botoes_mais_menos_respeitam_estoque(page):
    page.goto("/produto/12")  # Caixa Festa: 8 em estoque
    for _ in range(15):
        page.click(".qtd-mais")
    assert page.input_value("#quantidade") == "8"
    for _ in range(15):
        page.click(".qtd-menos")
    assert page.input_value("#quantidade") == "1"


def test_abas_cartao_e_pix(page):
    entrar(page)
    page.goto("/produto/4")
    page.click("text=Adicionar ao carrinho")
    page.goto("/checkout?tipo_entrega=RETIRADA")
    page.click("text=Ir para o pagamento")
    assert page.is_visible("#aba-cartao") and not page.is_visible("#aba-pix")
    page.click("text=⚡ PIX")
    assert page.is_visible("#aba-pix") and not page.is_visible("#aba-cartao")


def test_mostrar_ocultar_senha(page):
    page.goto("/login")
    page.fill("#senha", "segredo123")
    assert page.get_attribute("#senha", "type") == "password"
    page.click(".ver-senha")
    assert page.get_attribute("#senha", "type") == "text"


def test_cancelar_pede_confirmacao(page):
    entrar(page)
    page.goto("/produto/6")
    page.click("text=Adicionar ao carrinho")
    page.goto("/checkout?tipo_entrega=RETIRADA")
    page.click("text=Ir para o pagamento")
    page.once("dialog", lambda d: d.dismiss())  # usuario clica em "Cancelar" na confirmacao
    page.click("text=Cancelar pedido")
    assert "/pagamento" in page.url
    page.once("dialog", lambda d: d.accept())
    page.click("text=Cancelar pedido")
    ver(page, "Pedido cancelado")


# ------------------------------------------------------------------ entradas erradas
def test_cadastro_vazio_mostra_erros(page):
    page.goto("/cadastro")
    page.click("form.formulario button.btn-primario")
    texto = page.inner_text(".mensagens")
    assert "nome completo" in texto and "e-mail válido" in texto and "LGPD" in texto


def test_cep_com_letras_e_fora_da_area(page):
    entrar(page)
    page.goto("/conta/enderecos/novo")
    page.fill("#cep", "abcde")
    page.fill("#logradouro", "Av Paulista")
    page.fill("#numero", "1000")
    page.fill("#bairro", "Bela Vista")
    page.fill("#cidade", "São Paulo")
    page.fill("#uf", "SP")
    page.click("text=Salvar endereço")
    ver(page, "CEP deve ter 8 dígitos")
    page.fill("#cep", "")
    page.type("#cep", "01310100")
    page.click("text=Salvar endereço")
    page.goto("/produto/7")
    page.click("text=Adicionar ao carrinho")
    page.goto("/checkout")
    page.locator(".opcao", has_text="Av Paulista").click()
    ver(page, "Ainda não entregamos neste CEP")
    assert page.is_disabled("text=Ir para o pagamento")


def test_quantidade_zero_ou_negativa_remove_item(page):
    page.goto("/produto/9")
    page.click("text=Adicionar ao carrinho")
    page.goto("/carrinho/")
    campo = page.locator(".item-carrinho input[name=quantidade]")
    campo.fill("-3")
    campo.dispatch_event("change")
    page.wait_for_selector("text=Seu carrinho está vazio")


def test_cupom_invalido_e_expirado(page):
    page.goto("/produto/1")
    page.click("text=Adicionar ao carrinho")
    page.goto("/carrinho/")
    for codigo, msg in (("NAOEXISTE", "Cupom não encontrado"), ("EXPIRADO", "expirou"), ("DOCE15", "pedido mínimo")):
        page.fill("#codigo", codigo)
        page.click("text=Aplicar")
        ver(page, msg)


def test_produto_esgotado_nao_pode_ser_comprado(page):
    page.goto("/")
    card = page.locator(".card-produto", has_text="Nutella")
    assert "ESGOTADO" in card.inner_text() and card.locator(".btn-mais").count() == 0
    page.goto("/produto/8")
    assert page.is_disabled("text=Indisponível")


# ------------------------------------------------------------------ permissoes
def test_admin_sem_login_e_cliente_bloqueado(page):
    page.goto("/admin/")
    assert "/login" in page.url
    entrar(page)
    resp = page.goto("/admin/")
    assert resp.status == 403 and "Erro 403" in page.content()


def test_entregador_nao_ve_tela_de_compra(page):
    entrar(page, "entregador@sweetdreams.com", "Entrega@123")
    assert "/entregador" in page.url
    assert page.locator(".nav-inferior").count() == 0 and page.locator(".carrinho-topo").count() == 0


# ------------------------------------------------------------------ layout no celular
@pytest.mark.parametrize("rota", ["/", "/produto/1", "/carrinho/", "/login", "/cadastro", "/teste/"])
def test_sem_rolagem_horizontal_no_celular(page, rota):
    page.goto(rota)
    largura = page.evaluate("document.documentElement.scrollWidth")
    assert largura <= CELULAR["width"], f"{rota} tem {largura}px de largura"


# ------------------------------------------------------------------ ajustes do laudo do Yago
def test_botao_mais_nao_cobre_o_nome_do_produto(page):
    page.goto("/")
    card = page.locator(".card-produto").first
    botao = card.locator(".btn-mais").bounding_box()
    nome = card.locator("h2").bounding_box()
    sobrepoe = not (botao["y"] + botao["height"] <= nome["y"] or botao["x"] + botao["width"] <= nome["x"])
    assert not sobrepoe


def test_aviso_de_cep_aparece_enquanto_digita(page):
    entrar(page)
    page.goto("/conta/enderecos/novo")
    page.type("#cep", "01310100")
    ver(page, "ainda não entregamos nesse CEP")
    page.fill("#cep", "")
    page.type("#cep", "80010000")
    ver(page, "Entregamos nesse CEP")
