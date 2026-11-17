# Situação-Problema 2 - Desenvolvimento

## Tecnologias

- Python + Flask no back-end
- SQLite como banco
- HTML, CSS e JavaScript no front-end (sem framework)
- pytest para os testes

## Organização (MVC)

![Arquitetura](../diagramas/arquitetura.png)

- `app/models`: as classes que conversam com o banco (usuário, produto, pedido, cupom...)
- `app/templates` e `app/static`: as telas (views)
- `app/controllers`: as rotas, separadas por área (catálogo, carrinho, pedidos, admin, entregador...)
- `app/services`: regras que não dependem do banco (frete, pagamento e validações). Separei para conseguir testar sozinhas.

## Algumas decisões

- O pedido é gravado numa transação só. Se algum item estiver sem estoque, nada é salvo.
- O preço do item fica gravado no pedido, para que mudanças de preço depois não alterem pedidos antigos.
- O status do pedido segue uma ordem fixa (não dá para marcar como entregue um pedido que não foi pago, por exemplo).
- Produto não é apagado, só desativado, porque pode estar em pedidos antigos.
- A senha é salva com hash e do cartão só ficam os 4 últimos dígitos.
- Cada perfil (cliente, admin, entregador) só acessa as suas telas.

As telas estão na pasta [`docs/screenshots`](../screenshots/) e o passo a passo de uso no [manual](../manual-de-uso.md).
