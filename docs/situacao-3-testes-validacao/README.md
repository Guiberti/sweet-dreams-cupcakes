# Situação-Problema 3 - Testes, validação com usuários e correções

## 1. Estratégia (Modelo V)

| Lado da verificação | Nível de teste | Como foi feito |
|---|---|---|
| Requisitos (histórias de usuário) | **Teste de aceitação** | 5 testadores usam o app e preenchem o laudo (`/teste`) |
| Análise (casos de uso) | **Teste de sistema** | 20 testes automatizados que percorrem os fluxos completos pelas rotas HTTP |
| Arquitetura (MVC) | **Teste de integração** | 10 testes de Model + banco (transação, estoque, cupom, permissões) |
| Código | **Teste unitário** | 53 testes das regras puras (validações, frete, pagamento, totais, máquina de estados) |

- **Verificação** (estamos construindo certo?): testes automatizados + revisão das telas contra o protótipo do PIT I.
- **Validação** (construímos a coisa certa?): testes de aceitação com 5 pessoas reais.

## 2. Testes automatizados (pytest)

Comando: `python -m pytest -v`

**Resultado: 83 testes · 83 aprovados · 0 falhas · 10.1 s**

| Nível | Quantidade |
|---|---|
| Unitário | 53 |
| Integração | 10 |
| Sistema (ponta a ponta) | 20 |
| **Total** | **83** |

<details><summary>Lista completa dos 83 casos de teste</summary>

| # | Nível | Arquivo | Caso de teste | Resultado |
|---|---|---|---|---|
| 1 | Integração | `test_integracao_models.py` | `test_usuario_senha_guardada_com_hash` | Passou |
| 2 | Integração | `test_integracao_models.py` | `test_email_duplicado` | Passou |
| 3 | Integração | `test_integracao_models.py` | `test_criar_pedido_baixa_estoque_e_calcula_total` | Passou |
| 4 | Integração | `test_integracao_models.py` | `test_estoque_insuficiente_faz_rollback` | Passou |
| 5 | Integração | `test_integracao_models.py` | `test_retirada_zera_frete` | Passou |
| 6 | Integração | `test_integracao_models.py` | `test_entrega_exige_endereco` | Passou |
| 7 | Integração | `test_integracao_models.py` | `test_cancelamento_devolve_estoque` | Passou |
| 8 | Integração | `test_integracao_models.py` | `test_transicao_invalida_e_bloqueada` | Passou |
| 9 | Integração | `test_integracao_models.py` | `test_cupom_decrementa_quantidade` | Passou |
| 10 | Integração | `test_integracao_models.py` | `test_entregador_so_em_pedido_pago` | Passou |
| 11 | Sistema | `test_sistema_rotas.py` | `test_home_lista_produtos` | Passou |
| 12 | Sistema | `test_sistema_rotas.py` | `test_busca_e_filtro` | Passou |
| 13 | Sistema | `test_sistema_rotas.py` | `test_produto_inexistente_404` | Passou |
| 14 | Sistema | `test_sistema_rotas.py` | `test_cadastro_com_erros_mostra_mensagens` | Passou |
| 15 | Sistema | `test_sistema_rotas.py` | `test_cadastro_e_login` | Passou |
| 16 | Sistema | `test_sistema_rotas.py` | `test_login_invalido` | Passou |
| 17 | Sistema | `test_sistema_rotas.py` | `test_visitante_adiciona_ao_carrinho` | Passou |
| 18 | Sistema | `test_sistema_rotas.py` | `test_nao_adiciona_alem_do_estoque` | Passou |
| 19 | Sistema | `test_sistema_rotas.py` | `test_cupom_no_carrinho` | Passou |
| 20 | Sistema | `test_sistema_rotas.py` | `test_checkout_exige_login` | Passou |
| 21 | Sistema | `test_sistema_rotas.py` | `test_fluxo_compra_cartao_aprovado` | Passou |
| 22 | Sistema | `test_sistema_rotas.py` | `test_fluxo_compra_cartao_recusado` | Passou |
| 23 | Sistema | `test_sistema_rotas.py` | `test_fluxo_compra_pix` | Passou |
| 24 | Sistema | `test_sistema_rotas.py` | `test_cliente_nao_ve_pedido_de_outro` | Passou |
| 25 | Sistema | `test_sistema_rotas.py` | `test_area_admin_bloqueada_para_cliente` | Passou |
| 26 | Sistema | `test_sistema_rotas.py` | `test_admin_cadastra_produto` | Passou |
| 27 | Sistema | `test_sistema_rotas.py` | `test_admin_produto_invalido` | Passou |
| 28 | Sistema | `test_sistema_rotas.py` | `test_fluxo_admin_entregador_completo` | Passou |
| 29 | Sistema | `test_sistema_rotas.py` | `test_formulario_de_laudo` | Passou |
| 30 | Sistema | `test_sistema_rotas.py` | `test_formulario_de_laudo_vazio` | Passou |
| 31 | Unitário | `test_unit_frete_pagamento.py` | `test_frete_curitiba` | Passou |
| 32 | Unitário | `test_unit_frete_pagamento.py` | `test_frete_regiao_metropolitana` | Passou |
| 33 | Unitário | `test_unit_frete_pagamento.py` | `test_frete_gratis_acima_de_150` | Passou |
| 34 | Unitário | `test_unit_frete_pagamento.py` | `test_frete_fora_da_area` | Passou |
| 35 | Unitário | `test_unit_frete_pagamento.py` | `test_frete_cep_invalido` | Passou |
| 36 | Unitário | `test_unit_frete_pagamento.py` | `test_luhn[4111 1111 1111 1111-True]` | Passou |
| 37 | Unitário | `test_unit_frete_pagamento.py` | `test_luhn[5555555555554444-True]` | Passou |
| 38 | Unitário | `test_unit_frete_pagamento.py` | `test_luhn[4111111111111112-False]` | Passou |
| 39 | Unitário | `test_unit_frete_pagamento.py` | `test_luhn[1234-False]` | Passou |
| 40 | Unitário | `test_unit_frete_pagamento.py` | `test_bandeiras` | Passou |
| 41 | Unitário | `test_unit_frete_pagamento.py` | `test_validade_cartao[12/30-True]` | Passou |
| 42 | Unitário | `test_unit_frete_pagamento.py` | `test_validade_cartao[01/20-False]` | Passou |
| 43 | Unitário | `test_unit_frete_pagamento.py` | `test_validade_cartao[13/30-False]` | Passou |
| 44 | Unitário | `test_unit_frete_pagamento.py` | `test_validade_cartao[1230-False]` | Passou |
| 45 | Unitário | `test_unit_frete_pagamento.py` | `test_cartao_aprovado_guarda_somente_final` | Passou |
| 46 | Unitário | `test_unit_frete_pagamento.py` | `test_cartao_recusado` | Passou |
| 47 | Unitário | `test_unit_frete_pagamento.py` | `test_cartao_dados_invalidos` | Passou |
| 48 | Unitário | `test_unit_frete_pagamento.py` | `test_pix_contem_valor_e_pedido` | Passou |
| 49 | Unitário | `test_unit_regras_pedido.py` | `test_calcular_totais` | Passou |
| 50 | Unitário | `test_unit_regras_pedido.py` | `test_desconto_nunca_maior_que_produtos` | Passou |
| 51 | Unitário | `test_unit_regras_pedido.py` | `test_calculo_desconto[PERCENTUAL-10-100.0-10.0]` | Passou |
| 52 | Unitário | `test_unit_regras_pedido.py` | `test_calculo_desconto[VALOR_FIXO-15-100.0-15.0]` | Passou |
| 53 | Unitário | `test_unit_regras_pedido.py` | `test_calculo_desconto[VALOR_FIXO-15-10.0-10.0]` | Passou |
| 54 | Unitário | `test_unit_regras_pedido.py` | `test_maquina_de_estados[AGUARDANDO_PAGAMENTO-CONFIRMADO-ENTREGA-True]` | Passou |
| 55 | Unitário | `test_unit_regras_pedido.py` | `test_maquina_de_estados[AGUARDANDO_PAGAMENTO-ENTREGUE-ENTREGA-False]` | Passou |
| 56 | Unitário | `test_unit_regras_pedido.py` | `test_maquina_de_estados[CONFIRMADO-EM_PREPARO-ENTREGA-True]` | Passou |
| 57 | Unitário | `test_unit_regras_pedido.py` | `test_maquina_de_estados[EM_PREPARO-SAIU_PARA_ENTREGA-ENTREGA-True]` | Passou |
| 58 | Unitário | `test_unit_regras_pedido.py` | `test_maquina_de_estados[EM_PREPARO-ENTREGUE-ENTREGA-False]` | Passou |
| 59 | Unitário | `test_unit_regras_pedido.py` | `test_maquina_de_estados[EM_PREPARO-ENTREGUE-RETIRADA-True]` | Passou |
| 60 | Unitário | `test_unit_regras_pedido.py` | `test_maquina_de_estados[EM_PREPARO-SAIU_PARA_ENTREGA-RETIRADA-False]` | Passou |
| 61 | Unitário | `test_unit_regras_pedido.py` | `test_maquina_de_estados[ENTREGUE-CANCELADO-ENTREGA-False]` | Passou |
| 62 | Unitário | `test_unit_regras_pedido.py` | `test_maquina_de_estados[SAIU_PARA_ENTREGA-CANCELADO-ENTREGA-False]` | Passou |
| 63 | Unitário | `test_unit_regras_pedido.py` | `test_cupom_valido` | Passou |
| 64 | Unitário | `test_unit_regras_pedido.py` | `test_cupom_invalido[EXPIRADO-50.0-expirou]` | Passou |
| 65 | Unitário | `test_unit_regras_pedido.py` | `test_cupom_invalido[NAOEXISTE-50.0-n\xe3o encontrado]` | Passou |
| 66 | Unitário | `test_unit_regras_pedido.py` | `test_cupom_invalido[DOCE15-30.0-pedido m\xednimo]` | Passou |
| 67 | Unitário | `test_unit_regras_pedido.py` | `test_cupom_invalido[-30.0-Informe]` | Passou |
| 68 | Unitário | `test_unit_validacoes.py` | `test_validar_email[maria@gmail.com-True]` | Passou |
| 69 | Unitário | `test_unit_validacoes.py` | `test_validar_email[joao.silva+doces@empresa.com.br-True]` | Passou |
| 70 | Unitário | `test_unit_validacoes.py` | `test_validar_email[sem-arroba.com-False]` | Passou |
| 71 | Unitário | `test_unit_validacoes.py` | `test_validar_email[a@b-False]` | Passou |
| 72 | Unitário | `test_unit_validacoes.py` | `test_validar_email[-False]` | Passou |
| 73 | Unitário | `test_unit_validacoes.py` | `test_validar_email[maria @gmail.com-False]` | Passou |
| 74 | Unitário | `test_unit_validacoes.py` | `test_senha_valida_nao_gera_erros` | Passou |
| 75 | Unitário | `test_unit_validacoes.py` | `test_senha_invalida[Ab1-m\xednimo 8]` | Passou |
| 76 | Unitário | `test_unit_validacoes.py` | `test_senha_invalida[somenteletras-n\xfamero]` | Passou |
| 77 | Unitário | `test_unit_validacoes.py` | `test_senha_invalida[12345678-letra]` | Passou |
| 78 | Unitário | `test_unit_validacoes.py` | `test_validar_telefone[(41) 99999-0000-True]` | Passou |
| 79 | Unitário | `test_unit_validacoes.py` | `test_validar_telefone[4133334444-True]` | Passou |
| 80 | Unitário | `test_unit_validacoes.py` | `test_validar_telefone[9999-False]` | Passou |
| 81 | Unitário | `test_unit_validacoes.py` | `test_validar_cep` | Passou |
| 82 | Unitário | `test_unit_validacoes.py` | `test_cadastro_confirmacao_diferente` | Passou |
| 83 | Unitário | `test_unit_validacoes.py` | `test_cadastro_completo_valido` | Passou |

</details>

## 3. Defeitos encontrados na verificação e corrigidos

| # | Onde | Defeito | Como foi achado | Correção |
|---|---|---|---|---|
| D1 | `controllers/pedidos.py` | Pagamento com cartão quebrava com `TypeError` (o campo `status` era passado duas vezes para `Pagamento.registrar`) | 3 testes de sistema falharam na 1ª execução | Separar `status` dos dados extras antes de registrar |
| D2 | `tests/test_unit_validacoes.py` | Teste esperava o texto "mínimo de 8", mas a mensagem real é "no mínimo 8" | Teste unitário falhou | Ajustado o teste ao texto da regra (a regra estava certa) |
| D3 | Admin → Pedido | A lista de próximos status vinha em ordem alfabética: **"Cancelado" aparecia como opção padrão**, risco de cancelar pedido sem querer | Revisão visual das telas (screenshot) | Ordenar pela sequência do fluxo; "Cancelado" vai por último |
| D4 | Carrinho | Texto "BEMVINDO10aplicado" sem espaço | Revisão visual | Ajuste no template |
| D5 | Topo | Ícone do carrinho aparecia para admin e entregador, que não compram | Revisão visual | Carrinho só para cliente/visitante |

## 4. Testes de aceitação com 5 usuários

### 4.1 Como aplicar

1. Rode `python run.py` no computador e conecte os testadores **no mesmo Wi-Fi**; eles abrem no celular o endereço exibido no terminal (ex.: `http://192.168.0.10:5000`).
2. Entregue o **roteiro de tarefas** abaixo (pode mandar por WhatsApp).
3. Ao final, cada um preenche o laudo em **`/teste`** (link "Reportar teste / bug" no rodapé), anexando print se algo falhar.
4. Consulte os laudos em **Admin → Laudos de teste** e gere o PDF com **Ctrl+P → Salvar como PDF**.

### 4.2 Roteiro de tarefas para o testador

| # | Tarefa | Resultado esperado |
|---|---|---|
| T1 | Crie uma conta com seu e-mail | Conta criada e login automático |
| T2 | Tente criar outra conta com o mesmo e-mail | Mensagem "e-mail já cadastrado" |
| T3 | Busque "pistache" e filtre por "Veganos" | Lista filtrada corretamente |
| T4 | Adicione 2 cupcakes diferentes ao carrinho | Contador do carrinho atualiza |
| T5 | Aplique o cupom `BEMVINDO10`; depois tente `EXPIRADO` | Desconto de 10% / mensagem "expirou" |
| T6 | Cadastre um endereço com CEP `01310-100` | Aviso de fora da área de entrega |
| T7 | Cadastre um endereço com CEP `80010-000` e finalize | Frete de R$ 7,90 e total correto |
| T8 | Pague com o cartão `4000 0000 0000 0002` | Pagamento recusado com mensagem |
| T9 | Pague com `4111 1111 1111 1111`, validade `12/30`, CVV `123` | Pedido confirmado |
| T10 | Faça outro pedido com **Retirar na loja** e pague com **PIX** | Código PIX gerado e pedido confirmado |
| T11 | Acompanhe e cancele um pedido | Linha do tempo e cancelamento |
| T12 | (Opcional) Entre como admin, mude o status e atribua o entregador; entre como entregador e conclua a entrega | Status chega a "Entregue" para o cliente |

### 4.3 Modelo de laudo

Campos obrigatórios exigidos pela disciplina - todos presentes no formulário `/teste` e no modelo [`modelo-laudo-de-teste.docx`](modelo-laudo-de-teste.docx):

- Nome de quem testou · Data do teste
- O que testou e **funcionou**
- O que testou e **não funcionou** (e o que deve ser corrigido)
- Funcionalidade **não testada** (por que faltou)
- Sugestões de melhoria · Nota · Print da tela

### 4.4 Resultados dos testadores

> Preencher após os testes (o PDF com os 5 laudos vai em `laudos-testadores.pdf` nesta pasta).

| # | Testador | Perfil | Data | Funcionou | Não funcionou | Não testado | Nota |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |

### 4.5 Sugestões adotadas

| Sugestão | Testador | Adotada? | O que mudou |
|---|---|---|---|
| | | | |

## 5. Vídeo de apresentação

Roteiro de 5 minutos: [`roteiro-video.md`](roteiro-video.md)
