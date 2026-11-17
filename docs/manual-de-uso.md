# Manual de Uso - Sweet Dreams Cupcakes

## 1. Instalação

1. Instale o **Python 3.10+** (Windows: marque *Add Python to PATH*).
2. Abra o terminal na pasta do projeto e rode:
   ```bash
   pip install -r requirements.txt
   python run.py
   ```
3. Acesse `http://localhost:5000`. Para usar no celular, conecte-o no mesmo Wi-Fi e abra o endereço que aparece no terminal (ex.: `http://192.168.0.10:5000`).
   - No Windows, na primeira vez, o Firewall pode perguntar se o Python pode usar a rede: clique em **Permitir** (rede privada).

## 2. Cliente

| Tarefa | Como fazer |
|---|---|
| Criar conta | Toque em **Entrar → Cadastre-se**. Senha: mínimo 8 caracteres com letras e números. Aceite a política de privacidade (LGPD). |
| Encontrar um cupcake | Use a **busca** ou os **chips de categoria** (Clássicos, Gourmet, Veganos, Kits). Produtos esgotados aparecem em cinza no fim da lista. |
| Ver detalhes | Toque no card do produto: descrição, calorias e unidades disponíveis. |
| Adicionar ao carrinho | Botão **+** no card, ou escolha a quantidade no detalhe e toque **Adicionar ao carrinho**. Você pode montar o carrinho sem estar logado. |
| Ajustar carrinho | Na aba **Carrinho**, use **− / +** ou **Remover**. Quantidade 0 remove o item. |
| Cupom | Digite o código (ex.: `BEMVINDO10`) e toque **Aplicar**. Se não for válido, o app explica o motivo. |
| Finalizar | **Finalizar pedido** → escolha **Entrega em casa** (selecione/cadastre o endereço; o frete é calculado pelo CEP) ou **Retirar na loja** (grátis). |
| Pagar com cartão | Aba **Cartão de crédito**. Teste: `4111 1111 1111 1111`, validade `12/30`, CVV `123`. Para simular recusa: `4000 0000 0000 0002`. |
| Pagar com PIX | Aba **PIX → Gerar código PIX**. Copie o código. No ambiente de demonstração, toque **Simular pagamento PIX recebido**. |
| Acompanhar | Aba **Pedidos** → toque no pedido. A linha do tempo mostra: Aguardando pagamento → Confirmado → Em preparo → Saiu para entrega → Entregue. |
| Cancelar | Possível enquanto o pedido está *Aguardando pagamento* ou *Confirmado*. O estoque volta automaticamente. |
| Endereços | Aba **Conta** → adicionar, excluir ou tornar principal. |

**Área de entrega:** Curitiba (R$ 7,90, até 60 min) e Região Metropolitana (R$ 12,90, até 90 min). **Frete grátis** acima de R$ 150 em produtos.

## 3. Administrador (`admin@sweetdreams.com` / `Admin@123`)

| Tela | O que faz |
|---|---|
| **Dashboard** | Pedidos pagos, faturamento, ticket médio, pedidos aguardando preparo, mais vendidos, pedidos por status. |
| **Pedidos** | Lista com filtro por status. Ao abrir um pedido: avançar status (só as transições permitidas aparecem) e atribuir entregador. |
| **Produtos** | Cadastrar, editar (preço, estoque, cor, selo) e desativar. Produtos desativados somem do app mas continuam no histórico. |
| **Cupons** | Criar cupom percentual ou de valor fixo, com validade, mínimo e quantidade; ativar/desativar. |
| **Laudos de teste** | Todos os laudos enviados pelos testadores, com prints. Use **Ctrl+P → Salvar como PDF** para gerar o PDF de entrega. |

Fluxo de um pedido: *Confirmado* → **Em preparo** → atribuir entregador → (entregador) **Saiu para entrega** → **Entregue**. Para retirada: *Em preparo* → **Entregue** (retirado).

## 4. Entregador (`entregador@sweetdreams.com` / `Entrega@123`)

A tela **Minhas entregas** lista os pedidos atribuídos com cliente, endereço e valor.
- **Saí para entrega**: disponível quando o pedido está *Em preparo*.
- **Confirmar entrega**: disponível quando o pedido saiu para entrega.

## 5. Testadores (Situação-Problema 3)

Acesse **`/teste`** (link *Reportar teste / bug* no rodapé de todas as páginas) e preencha: nome, data, o que funcionou, o que não funcionou, o que não testou, sugestões, nota e print (opcional).

## 6. Mensagens de erro tratadas

| Situação | Mensagem |
|---|---|
| Login errado | "E-mail ou senha incorretos." |
| E-mail já usado | "Este e-mail já está cadastrado. Faça login ou recupere sua senha." |
| Estoque | "Só temos N unidade(s) de X no momento." |
| Cupom | "Este cupom expirou." / "Cupom não encontrado." / "Este cupom exige pedido mínimo de R$ X" |
| CEP fora da área | "Ainda não entregamos neste CEP. Escolha 'Retirar na loja'…" |
| Cartão | "Número do cartão inválido." / "Validade inválida ou cartão vencido" / "CVV deve ter 3 ou 4 dígitos." |
| Recusa | "Pagamento recusado: … Tente outro cartão ou pague com PIX." |
| Página inexistente / sem permissão | Telas de erro 404 e 403 com botão para voltar ao início |
