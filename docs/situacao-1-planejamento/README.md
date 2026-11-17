# Situação-Problema 1 - Revisão do planejamento e banco de dados

Antes de começar a programar, revisei o que eu tinha entregado no PIT I. Algumas coisas estavam incompletas e foram corrigidas aqui.

## O que mudou no escopo

Mantive todas as histórias de prioridade A e B do backlog. Avaliar produto, favoritos e notificações ficaram para depois.

Outras mudanças:

- O app virou um **site responsivo** em vez de app nativo, porque a disciplina pede HTML/CSS/JS e assim qualquer pessoa testa pelo celular sem instalar nada.
- Adicionei a opção de **retirar na loja**. A entrega só cobre Curitiba e região (cupcake não aguenta viagem longa), então quem mora longe não conseguia comprar.
- O frete agora tem uma regra definida por faixa de CEP, com frete grátis acima de R$ 150. No PIT I eu só tinha escrito "calculado por API".
- O cadastro pede o aceite da LGPD (estava nos requisitos não funcionais, mas nenhuma tela pedia).
- Tirei o login com Google/Facebook do MVP.
- O pagamento é simulado, porque integrar com um gateway real precisaria de contrato.
- O entregador ganhou uma tela própria (antes ele só aparecia no caso de uso).

## Correções na UML

O principal problema era o **diagrama de classes do PIT I, que estava sem as linhas de relacionamento**. Refiz o diagrama com as associações e multiplicidades ([classes.png](../diagramas/classes.png)) e incluí as classes Pagamento e HistoricoStatus.

Também fiz o diagrama de atividades que eu tinha citado no PIT I mas não entreguei ([atividades.png](../diagramas/atividades.png)), um diagrama de estados do pedido ([estados.png](../diagramas/estados.png)) e o da arquitetura ([arquitetura.png](../diagramas/arquitetura.png)). Os diagramas antigos ficaram em `diagramas/pit1-original` para comparação.

Outros ajustes no modelo: o pedido passou a guardar uma cópia do endereço (se o cliente apagar o endereço depois, o pedido antigo não perde a informação) e o subtotal do item deixou de ser gravado, porque dá para calcular.

## Interface

Mantive o visual do PIT I (fundo escuro e rosa). A barra de baixo ficou com 4 abas e as categorias viraram filtros na tela inicial. Coloquei mensagem de erro em todos os formulários e telas de erro para 403, 404 e 500.

## Banco de dados

- Modelo normalizado até a 3FN, com 10 tabelas.
- SGBD: SQLite (já vem com o Python e não precisa instalar servidor).
- Script: [`database/schema.sql`](../../database/schema.sql)
- DER: [der.png](../diagramas/der.png)
- [Dicionário de dados](dicionario-de-dados.md)
