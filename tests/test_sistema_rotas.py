# testes de sistema: fluxos completos pelas rotas
from conftest import login


def texto(resp):
    return resp.get_data(as_text=True)


# ------------------------- Catálogo e autenticação -------------------------
def test_home_lista_produtos(client):
    r = client.get("/")
    assert r.status_code == 200 and "Red Velvet" in texto(r) and "ESGOTADO" in texto(r)


def test_busca_e_filtro(client):
    assert "Pistache" in texto(client.get("/?busca=pistache"))
    r = texto(client.get("/?categoria=3"))
    assert "Limão Vegano" in r and "Red Velvet" not in r


def test_busca_com_filtro_errado_mostra_outras_categorias(client):
    # caso do laudo: "pistache" com o filtro Veganos ligado
    t = texto(client.get("/?busca=pistache&categoria=3"))
    assert "Não encontramos" in t and "Pistache" in t


def test_produto_inexistente_404(client):
    r = client.get("/produto/999")
    assert r.status_code == 404 and "Ops!" in texto(r)


def test_cadastro_com_erros_mostra_mensagens(client):
    r = client.post("/cadastro", data={"nome": "A", "email": "x", "senha": "123", "confirmacao": "456"})
    t = texto(r)
    assert "Informe seu nome completo" in t and "e-mail válido" in t and "LGPD" in t


def test_cadastro_e_login(client):
    dados = {"nome": "Bruna Costa", "email": "bruna@teste.com", "telefone": "41988887777",
             "senha": "Cupcake1", "confirmacao": "Cupcake1", "aceite_lgpd": "on"}
    r = client.post("/cadastro", data=dados, follow_redirects=True)
    assert "Conta criada com sucesso" in texto(r)
    client.get("/logout")
    assert login(client, "bruna@teste.com", "Cupcake1").status_code == 302


def test_login_invalido(client):
    r = login(client, "cliente@teste.com", "errada")
    assert r.status_code == 401 and "E-mail ou senha incorretos" in texto(r)


# ------------------------------ Carrinho ------------------------------
def test_visitante_adiciona_ao_carrinho(client):
    client.post("/carrinho/adicionar/1", data={"quantidade": 2})
    r = texto(client.get("/carrinho/"))
    assert "Red Velvet" in r and "R$ 25,80" in r


def test_nao_adiciona_alem_do_estoque(client):
    r = client.post("/carrinho/adicionar/5", data={"quantidade": 999}, follow_redirects=True)
    assert "Só temos 15" in texto(r)


def test_cupom_no_carrinho(client):
    client.post("/carrinho/adicionar/1", data={"quantidade": 1})
    assert "aplicado" in texto(client.post("/carrinho/cupom", data={"codigo": "bemvindo10"}, follow_redirects=True))
    assert "expirou" in texto(client.post("/carrinho/cupom", data={"codigo": "EXPIRADO"}, follow_redirects=True))


def test_cupom_continua_depois_do_login(client):
    client.post("/carrinho/adicionar/1")
    client.post("/carrinho/cupom", data={"codigo": "BEMVINDO10"})
    login(client, "cliente@teste.com", "Cliente@123")
    assert "BEMVINDO10" in texto(client.get("/checkout"))


def test_checkout_exige_login(client):
    client.post("/carrinho/adicionar/1")
    r = client.get("/checkout")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


# ---------------------------- Compra completa ----------------------------
def _comprar(c, qtd=2):
    c.post("/carrinho/adicionar/1", data={"quantidade": qtd})
    r = c.post("/checkout", data={"tipo_entrega": "ENTREGA", "endereco_id": 1})
    assert r.status_code == 302
    return r.headers["Location"]  # /pedido/<id>/pagamento


def test_fluxo_compra_cartao_aprovado(cliente_logado):
    url = _comprar(cliente_logado)
    r = cliente_logado.post(url, data={"forma": "CARTAO", "numero": "4111 1111 1111 1111",
                                       "nome_cartao": "CLIENTE TESTE", "validade": "12/30", "cvv": "123"},
                            follow_redirects=True)
    t = texto(r)
    assert "Pagamento aprovado" in t and "Pagamento confirmado" in t and "final 1111" in t


def test_fluxo_compra_cartao_recusado(cliente_logado):
    url = _comprar(cliente_logado)
    r = cliente_logado.post(url, data={"forma": "CARTAO", "numero": "4000 0000 0000 0002",
                                       "nome_cartao": "CLIENTE TESTE", "validade": "12/30", "cvv": "123"})
    assert "Pagamento recusado" in texto(r)


def test_fluxo_compra_pix(cliente_logado):
    url = _comprar(cliente_logado)
    r = cliente_logado.post(url, data={"forma": "PIX"}, follow_redirects=True)
    assert "PIX copia e cola" in texto(r)
    pid = url.split("/")[2]
    r = cliente_logado.post(f"/pedido/{pid}/pix/confirmar", follow_redirects=True)
    assert "PIX recebido" in texto(r)


def test_cliente_nao_ve_pedido_de_outro(client, app):
    login(client, "cliente@teste.com", "Cliente@123")
    url = _comprar(client)
    client.get("/logout")
    client.post("/cadastro", data={"nome": "Intruso", "email": "x@x.com", "senha": "Intruso1",
                                   "confirmacao": "Intruso1", "aceite_lgpd": "on"})
    assert client.get(url.replace("/pagamento", "")).status_code == 403


# ------------------------- Admin e entregador -------------------------
def test_area_admin_bloqueada_para_cliente(cliente_logado):
    assert cliente_logado.get("/admin/").status_code == 403


def test_admin_cadastra_produto(admin_logado):
    r = admin_logado.post("/admin/produtos/novo", data={"nome": "Café Gourmet", "categoria_id": 2, "preco": "15,50",
                                                         "estoque": 10, "cor": "#6F4E37", "ativo": "1"},
                          follow_redirects=True)
    assert "Produto cadastrado" in texto(r) and "Café Gourmet" in texto(r)


def test_admin_produto_invalido(admin_logado):
    r = admin_logado.post("/admin/produtos/novo", data={"nome": "X", "categoria_id": 99, "preco": "-1", "estoque": "a"})
    t = texto(r)
    assert "pelo menos 3" in t and "maior que zero" in t and "inteiro" in t


def test_fluxo_admin_entregador_completo(client):
    login(client, "cliente@teste.com", "Cliente@123")
    url = _comprar(client, 1)
    pid = int(url.split("/")[2])
    client.post(url, data={"forma": "CARTAO", "numero": "4111111111111111", "nome_cartao": "CLIENTE",
                           "validade": "12/30", "cvv": "123"})
    client.get("/logout")

    login(client, "admin@sweetdreams.com", "Admin@123")
    client.post(f"/admin/pedidos/{pid}", data={"acao": "status", "status": "EM_PREPARO"})
    client.post(f"/admin/pedidos/{pid}", data={"acao": "entregador", "entregador_id": 2})
    client.get("/logout")

    login(client, "entregador@sweetdreams.com", "Entrega@123")
    assert f"SD{pid:06d}" in texto(client.get("/entregador/"))
    client.post(f"/entregador/pedido/{pid}/status", data={"status": "SAIU_PARA_ENTREGA"})
    r = client.post(f"/entregador/pedido/{pid}/status", data={"status": "ENTREGUE"}, follow_redirects=True)
    assert "Entrega atualizada" in texto(r)
    client.get("/logout")

    login(client, "cliente@teste.com", "Cliente@123")
    assert "Entregue" in texto(client.get(f"/pedido/{pid}"))


# ------------------------------ Laudo de teste ------------------------------
def test_formulario_de_laudo(client, admin_logado):
    r = client.post("/teste/", data={"nome_testador": "Pedro Alves", "data_teste": "2026-11-17",
                                     "funcionou": "Cadastro e carrinho", "nota": "5"}, follow_redirects=True)
    assert "Laudo enviado" in texto(r)
    login(client, "admin@sweetdreams.com", "Admin@123")
    assert "Pedro Alves" in texto(client.get("/admin/laudos"))


def test_admin_exclui_laudo(client):
    client.post("/teste/", data={"nome_testador": "Teste Brincadeira", "data_teste": "2026-11-17", "funcionou": "x"})
    login(client, "admin@sweetdreams.com", "Admin@123")
    assert "Teste Brincadeira" in texto(client.get("/admin/laudos"))
    r = client.post("/admin/laudos/1/excluir", follow_redirects=True)
    assert "Laudo excluído" in texto(r) and "Teste Brincadeira" not in texto(r)


def test_formulario_de_laudo_vazio(client):
    assert "Informe seu nome" in texto(client.post("/teste/", data={}))


def test_data_mostrada_no_horario_de_brasilia(app):
    formatar = app.jinja_env.filters["data"]
    assert formatar("2026-11-17 02:03:00") == "16/11/2026 23:03"  # banco guarda em UTC
    assert formatar("2026-11-17", "%d/%m/%Y") == "17/11/2026"     # data sem hora nao muda


# ---------------------------- melhorias do laudo do Matheus ----------------------------
def test_cupom_so_pode_ser_usado_uma_vez_por_cliente(cliente_logado):
    cliente_logado.post("/carrinho/adicionar/1")
    cliente_logado.post("/carrinho/cupom", data={"codigo": "BEMVINDO10"})
    cliente_logado.post("/checkout", data={"tipo_entrega": "RETIRADA"})
    cliente_logado.post("/carrinho/adicionar/2")
    r = cliente_logado.post("/carrinho/cupom", data={"codigo": "BEMVINDO10"}, follow_redirects=True)
    assert "já usou este cupom" in texto(r)


def test_novo_endereco_volta_selecionado_e_avisa_fora_da_area(cliente_logado):
    cliente_logado.post("/carrinho/adicionar/1")
    dados = {"cep": "01310100", "logradouro": "Av Paulista", "numero": "1", "bairro": "Bela Vista",
             "cidade": "São Paulo", "uf": "SP"}
    r = cliente_logado.post("/conta/enderecos/novo?voltar=checkout", data=dados)
    assert "endereco_id=2" in r.headers["Location"]
    t = texto(cliente_logado.get(r.headers["Location"]))
    assert "ainda não entregamos neste CEP" in t


def test_cancelar_pedido_pago_avisa_estorno(cliente_logado):
    url = _comprar(cliente_logado, 1)
    cliente_logado.post(url, data={"forma": "PIX"})
    pid = url.split("/")[2]
    cliente_logado.post(f"/pedido/{pid}/pix/confirmar")
    r = cliente_logado.post(f"/pedido/{pid}/cancelar", follow_redirects=True)
    assert "estornado" in texto(r) and "estorno solicitado" in texto(r)


# ---------------------------- sugestao do laudo do Guylherme ----------------------------
def test_carrinho_mostra_quanto_falta_para_frete_gratis(client):
    client.post("/carrinho/adicionar/12")  # Caixa Festa R$ 129,90
    assert "Faltam" in texto(client.get("/carrinho/")) and "R$ 20,10" in texto(client.get("/carrinho/"))
    client.post("/carrinho/adicionar/1", data={"quantidade": 2})  # + 25,80 = 155,70
    assert "ganhou frete grátis" in texto(client.get("/carrinho/"))
