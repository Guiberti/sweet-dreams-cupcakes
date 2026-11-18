# Situação-Problema 3 - Testes e validação

## Testes automatizados

São 113 testes e todos passam.

Testes do servidor (`python -m pytest tests --ignore=tests/e2e`):

- 53 unitários (validações, frete, pagamento, cálculo do total, cupom, status do pedido)
- 10 de integração (model + banco: estoque, transação, cupom)
- 28 de sistema (fluxos completos pelas rotas: cadastro, compra, admin, entregador)

Testes de interface no navegador (`tests/e2e`): 22 testes que abrem o Chrome de verdade, em tamanho de celular, e usam o site como uma pessoa usaria. Eles testam também o JavaScript da tela (máscaras, botões + e -, abas de pagamento, confirmação antes de cancelar), entradas erradas (cadastro vazio, CEP com letras, quantidade negativa, cupons inválidos), as permissões e se nenhuma página fica mais larga que a tela do celular. Cada teste salva um print em [`e2e/`](e2e/).

Para rodar os de interface: `pip install -r requirements-dev.txt`, `playwright install chromium` e `python -m pytest tests/e2e -v`.

<details><summary>Lista dos testes</summary>

- `test_interface.py::test_compra_completa_pela_interface`
- `test_interface.py::test_pagamento_recusado_e_depois_pix`
- `test_interface.py::test_mascaras_de_entrada`
- `test_interface.py::test_botoes_mais_menos_respeitam_estoque`
- `test_interface.py::test_abas_cartao_e_pix`
- `test_interface.py::test_mostrar_ocultar_senha`
- `test_interface.py::test_cancelar_pede_confirmacao`
- `test_interface.py::test_cadastro_vazio_mostra_erros`
- `test_interface.py::test_cep_com_letras_e_fora_da_area`
- `test_interface.py::test_quantidade_zero_ou_negativa_remove_item`
- `test_interface.py::test_cupom_invalido_e_expirado`
- `test_interface.py::test_produto_esgotado_nao_pode_ser_comprado`
- `test_interface.py::test_admin_sem_login_e_cliente_bloqueado`
- `test_interface.py::test_entregador_nao_ve_tela_de_compra`
- `test_interface.py::test_sem_rolagem_horizontal_no_celular[/]`
- `test_interface.py::test_sem_rolagem_horizontal_no_celular[/produto/1]`
- `test_interface.py::test_sem_rolagem_horizontal_no_celular[/carrinho/]`
- `test_interface.py::test_sem_rolagem_horizontal_no_celular[/login]`
- `test_interface.py::test_sem_rolagem_horizontal_no_celular[/cadastro]`
- `test_interface.py::test_sem_rolagem_horizontal_no_celular[/teste/]`
- `test_interface.py::test_botao_mais_nao_cobre_o_nome_do_produto`
- `test_interface.py::test_aviso_de_cep_aparece_enquanto_digita`
- `test_integracao_models.py::test_usuario_senha_guardada_com_hash`
- `test_integracao_models.py::test_email_duplicado`
- `test_integracao_models.py::test_criar_pedido_baixa_estoque_e_calcula_total`
- `test_integracao_models.py::test_estoque_insuficiente_faz_rollback`
- `test_integracao_models.py::test_retirada_zera_frete`
- `test_integracao_models.py::test_entrega_exige_endereco`
- `test_integracao_models.py::test_cancelamento_devolve_estoque`
- `test_integracao_models.py::test_transicao_invalida_e_bloqueada`
- `test_integracao_models.py::test_cupom_decrementa_quantidade`
- `test_integracao_models.py::test_entregador_so_em_pedido_pago`
- `test_sistema_rotas.py::test_home_lista_produtos`
- `test_sistema_rotas.py::test_busca_e_filtro`
- `test_sistema_rotas.py::test_busca_com_filtro_errado_mostra_outras_categorias`
- `test_sistema_rotas.py::test_produto_inexistente_404`
- `test_sistema_rotas.py::test_cadastro_com_erros_mostra_mensagens`
- `test_sistema_rotas.py::test_cadastro_e_login`
- `test_sistema_rotas.py::test_login_invalido`
- `test_sistema_rotas.py::test_visitante_adiciona_ao_carrinho`
- `test_sistema_rotas.py::test_nao_adiciona_alem_do_estoque`
- `test_sistema_rotas.py::test_cupom_no_carrinho`
- `test_sistema_rotas.py::test_cupom_continua_depois_do_login`
- `test_sistema_rotas.py::test_checkout_exige_login`
- `test_sistema_rotas.py::test_fluxo_compra_cartao_aprovado`
- `test_sistema_rotas.py::test_fluxo_compra_cartao_recusado`
- `test_sistema_rotas.py::test_fluxo_compra_pix`
- `test_sistema_rotas.py::test_cliente_nao_ve_pedido_de_outro`
- `test_sistema_rotas.py::test_area_admin_bloqueada_para_cliente`
- `test_sistema_rotas.py::test_admin_cadastra_produto`
- `test_sistema_rotas.py::test_admin_produto_invalido`
- `test_sistema_rotas.py::test_fluxo_admin_entregador_completo`
- `test_sistema_rotas.py::test_formulario_de_laudo`
- `test_sistema_rotas.py::test_admin_exclui_laudo`
- `test_sistema_rotas.py::test_formulario_de_laudo_vazio`
- `test_sistema_rotas.py::test_data_mostrada_no_horario_de_brasilia`
- `test_sistema_rotas.py::test_cupom_so_pode_ser_usado_uma_vez_por_cliente`
- `test_sistema_rotas.py::test_novo_endereco_volta_selecionado_e_avisa_fora_da_area`
- `test_sistema_rotas.py::test_cancelar_pedido_pago_avisa_estorno`
- `test_sistema_rotas.py::test_carrinho_mostra_quanto_falta_para_frete_gratis`
- `test_unit_frete_pagamento.py::test_frete_curitiba`
- `test_unit_frete_pagamento.py::test_frete_regiao_metropolitana`
- `test_unit_frete_pagamento.py::test_frete_gratis_acima_de_150`
- `test_unit_frete_pagamento.py::test_frete_fora_da_area`
- `test_unit_frete_pagamento.py::test_frete_cep_invalido`
- `test_unit_frete_pagamento.py::test_luhn[4111 1111 1111 1111-True]`
- `test_unit_frete_pagamento.py::test_luhn[5555555555554444-True]`
- `test_unit_frete_pagamento.py::test_luhn[4111111111111112-False]`
- `test_unit_frete_pagamento.py::test_luhn[1234-False]`
- `test_unit_frete_pagamento.py::test_bandeiras`
- `test_unit_frete_pagamento.py::test_validade_cartao[12/30-True]`
- `test_unit_frete_pagamento.py::test_validade_cartao[01/20-False]`
- `test_unit_frete_pagamento.py::test_validade_cartao[13/30-False]`
- `test_unit_frete_pagamento.py::test_validade_cartao[1230-False]`
- `test_unit_frete_pagamento.py::test_cartao_aprovado_guarda_somente_final`
- `test_unit_frete_pagamento.py::test_cartao_recusado`
- `test_unit_frete_pagamento.py::test_cartao_dados_invalidos`
- `test_unit_frete_pagamento.py::test_pix_contem_valor_e_pedido`
- `test_unit_regras_pedido.py::test_calcular_totais`
- `test_unit_regras_pedido.py::test_desconto_nunca_maior_que_produtos`
- `test_unit_regras_pedido.py::test_calculo_desconto[PERCENTUAL-10-100.0-10.0]`
- `test_unit_regras_pedido.py::test_calculo_desconto[VALOR_FIXO-15-100.0-15.0]`
- `test_unit_regras_pedido.py::test_calculo_desconto[VALOR_FIXO-15-10.0-10.0]`
- `test_unit_regras_pedido.py::test_maquina_de_estados[AGUARDANDO_PAGAMENTO-CONFIRMADO-ENTREGA-True]`
- `test_unit_regras_pedido.py::test_maquina_de_estados[AGUARDANDO_PAGAMENTO-ENTREGUE-ENTREGA-False]`
- `test_unit_regras_pedido.py::test_maquina_de_estados[CONFIRMADO-EM_PREPARO-ENTREGA-True]`
- `test_unit_regras_pedido.py::test_maquina_de_estados[EM_PREPARO-SAIU_PARA_ENTREGA-ENTREGA-True]`
- `test_unit_regras_pedido.py::test_maquina_de_estados[EM_PREPARO-ENTREGUE-ENTREGA-False]`
- `test_unit_regras_pedido.py::test_maquina_de_estados[EM_PREPARO-ENTREGUE-RETIRADA-True]`
- `test_unit_regras_pedido.py::test_maquina_de_estados[EM_PREPARO-SAIU_PARA_ENTREGA-RETIRADA-False]`
- `test_unit_regras_pedido.py::test_maquina_de_estados[ENTREGUE-CANCELADO-ENTREGA-False]`
- `test_unit_regras_pedido.py::test_maquina_de_estados[SAIU_PARA_ENTREGA-CANCELADO-ENTREGA-False]`
- `test_unit_regras_pedido.py::test_cupom_valido`
- `test_unit_regras_pedido.py::test_cupom_invalido[EXPIRADO-50.0-expirou]`
- `test_unit_regras_pedido.py::test_cupom_invalido[NAOEXISTE-50.0-n\xe3o encontrado]`
- `test_unit_regras_pedido.py::test_cupom_invalido[DOCE15-30.0-pedido m\xednimo]`
- `test_unit_regras_pedido.py::test_cupom_invalido[-30.0-Informe]`
- `test_unit_validacoes.py::test_validar_email[maria@gmail.com-True]`
- `test_unit_validacoes.py::test_validar_email[joao.silva+doces@empresa.com.br-True]`
- `test_unit_validacoes.py::test_validar_email[sem-arroba.com-False]`
- `test_unit_validacoes.py::test_validar_email[a@b-False]`
- `test_unit_validacoes.py::test_validar_email[-False]`
- `test_unit_validacoes.py::test_validar_email[maria @gmail.com-False]`
- `test_unit_validacoes.py::test_senha_valida_nao_gera_erros`
- `test_unit_validacoes.py::test_senha_invalida[Ab1-m\xednimo 8]`
- `test_unit_validacoes.py::test_senha_invalida[somenteletras-n\xfamero]`
- `test_unit_validacoes.py::test_senha_invalida[12345678-letra]`
- `test_unit_validacoes.py::test_validar_telefone[(41) 99999-0000-True]`
- `test_unit_validacoes.py::test_validar_telefone[4133334444-True]`
- `test_unit_validacoes.py::test_validar_telefone[9999-False]`
- `test_unit_validacoes.py::test_validar_cep`
- `test_unit_validacoes.py::test_cadastro_confirmacao_diferente`
- `test_unit_validacoes.py::test_cadastro_completo_valido`

</details>

## Problemas que encontrei e corrigi

1. O pagamento com cartão dava erro (`TypeError`) porque o status era passado duas vezes ao salvar o pagamento. Os testes de sistema pegaram isso na primeira vez que rodei.
2. Um teste comparava a mensagem errada da senha ("mínimo de 8" em vez de "no mínimo 8"). Arrumei o teste.
3. Na tela do pedido no admin, "Cancelado" aparecia como primeira opção de status, o que facilitava cancelar sem querer. Agora as opções seguem a ordem do fluxo.
4. Faltava um espaço no texto do cupom aplicado no carrinho.
5. O ícone do carrinho aparecia para o admin e o entregador, que não compram nada.
6. Cupom sumia no login: quem aplicava o cupom antes de entrar na conta perdia o desconto depois do login (o carrinho era mantido, o cupom não). Achado pelo teste de interface da compra completa.
7. Abas de pagamento: ao clicar em PIX, o formulário do cartão continuava aparecendo embaixo, porque o CSS do formulário anulava o atributo `hidden`. Achado pelo teste de interface das abas.
8. Horário errado: os pedidos mostravam o horário 3 horas adiantado, porque o SQLite grava a data em UTC. Agora a data é convertida para o horário de Brasília. Percebi olhando os prints dos testes de interface.

Os erros 6 e 7 não apareciam nos testes do servidor, só no navegador.

## Testes com usuários

Cinco pessoas testaram o app pelo celular, conectadas na mesma rede do meu computador. Cada uma seguiu o roteiro abaixo e preencheu o laudo no próprio app (`/teste`, link no rodapé). Também deixei um [modelo em Word](modelo-laudo-de-teste.docx) para quem preferir.

Roteiro passado para os testadores:

1. Criar uma conta (e tentar criar outra com o mesmo e-mail)
2. Buscar "pistache" e filtrar por "Veganos"
3. Colocar 2 produtos no carrinho
4. Testar os cupons `BEMVINDO10` e `EXPIRADO`
5. Cadastrar um endereço com CEP `01310-100` (fora da área) e depois com `80010-000`
6. Pagar com o cartão `4000 0000 0000 0002` (deve recusar) e depois com `4111 1111 1111 1111`, validade `12/30`, CVV `123`
7. Fazer outro pedido com retirada na loja e pagar com PIX
8. Acompanhar e cancelar um pedido

### Resultados

Recebi 5 laudos. O PDF com todos eles e os prints está em [laudos-testadores.pdf](laudos-testadores.pdf).

| # | Testador | Perfil | Data | Resumo | Nota |
|---|---|---|---|---|---|
| 1 | André Dudu Berti | irmão | 16/11 | Testou produtos, cupons, compra, e-mail repetido e CEP. Não achou problemas. | 4/5 |
| 2 | Marcio | (não informado) | 17/11 | Buscou "pistache" com o filtro Veganos ligado e não encontrou nada; achou que era erro. Não finalizou a compra. | 4/5 |
| 3 | Matheus Gonçalves | desenvolvedor | 17/11 | Fluxo completo funcionou. Achou 5 problemas: endereço novo não vinha selecionado, endereço fora da área salvo sem aviso, cupom de boas-vindas usado duas vezes, cancelamento de pedido pago sem estorno e falta de favicon. | 4/5 |
| 4 | Guylherme Somnezi | desenvolvedor | 17/11 | Categorias, esgotado e frete grátis funcionaram. Achou que a barra de baixo ocupa espaço em telas pequenas. | 4/5 |
| 5 | Yago Rosa | barbeiro (usuário final) | 17/11 | Testou depois das correções e confirmou que elas funcionaram. Achou o botão "+" cobrindo o nome dos cupcakes no celular. | 4/5 |

### O que mudei depois dos testes

| Laudo | Problema ou sugestão | O que fiz |
|---|---|---|
| Marcio | Busca com filtro de categoria não achava nada | O app avisa e mostra o resultado das outras categorias |
| Matheus | Endereço novo não vinha selecionado no checkout | Volta para o checkout com o endereço novo marcado |
| Matheus | Endereço fora da área salvo sem aviso | Avisa ao salvar e também enquanto digita o CEP |
| Matheus | Cupom BEMVINDO10 funcionou duas vezes | Cada cliente usa o cupom uma vez |
| Matheus | Pedido pago cancelado continuava "aprovado" | Mostra "estorno solicitado (até 7 dias úteis)" |
| Matheus | Sem favicon | Coloquei o ícone de cupcake |
| Matheus | Esconder o cartão depois de gerar o PIX / avisar ao remover cupom / mostrar frete no carrinho / "+" maior | Feito |
| Guylherme | Mostrar quanto falta para o frete grátis | "Faltam R$ X para ganhar frete grátis" no carrinho |
| Guylherme | Barra de baixo ocupa espaço | Ela some ao rolar para baixo e volta ao rolar para cima |
| Guylherme | Botão de adicionar direto no card | Já existia (o "+"), mas estava discreto; ficou maior |
| Yago | Botão "+" cobrindo o nome no celular | Erro que eu mesmo criei ao aumentar o botão. Mudei ele para o canto da imagem e criei um teste que confere que ele não cobre o nome |
| Matheus e Yago | Preencher rua e bairro pelo CEP | O formulário busca o endereço no ViaCEP quando o CEP é digitado (se não houver internet, preenche à mão) |
| Yago | Botão de confirmar o PIX visível sem rolar | Botão logo abaixo do QR Code |

O laudo do Yago foi feito depois das correções do Matheus e confirmou que elas funcionaram (endereço selecionado, cupom bloqueado no segundo pedido, aviso de estorno).

## Vídeo

Apresentação do sistema funcionando: https://youtu.be/0dnbPPl65Ds
