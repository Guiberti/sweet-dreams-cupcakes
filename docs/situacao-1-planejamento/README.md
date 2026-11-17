# Situação-Problema 1 - Atualizar o plano de projeto e o banco de dados

Ciclo de melhoria contínua (Kaizen) sobre o que foi entregue no PIT I.

## 1. Escopo revisado (MVP)

O PIT I listou 22 histórias de usuário (122 pontos). Para o PIT II, o escopo foi **revalidado** com base na prioridade MoSCoW já definida:

| Prioridade | Histórias | Decisão no PIT II |
|---|---|---|
| A (Must) | 001, 002, 003, 004, 005, 006, 008, 009, 010, 011, 012, 018, 019, 022 | **Implementadas** |
| B (Should) | 007, 013, 015, 020, 021 | **Implementadas** |
| C (Could) | 014 Avaliar produto, 017 Notificações push | Adiadas (próxima release) |
| D (Won't) | 016 Favoritos | Fora do MVP |

**Mudanças de escopo e por quê:**

| # | Mudança | Motivo |
|---|---|---|
| 1 | De "app mobile nativo" para **app web mobile-first** (abre no navegador do celular) | A disciplina pede front-end em HTML/CSS/JS; o app web roda em qualquer celular sem instalação, o que facilita os testes com 5 usuários (Situação 3). |
| 2 | **Retirada na loja** como opção de entrega | Cupcake é perecível e a entrega só cobre Curitiba e RMC; sem retirada, clientes de fora da área não conseguiam comprar. |
| 3 | **Área de entrega por faixa de CEP** com frete grátis ≥ R$ 150 | No PIT I o frete era "calculado por API"; a regra concreta foi definida para poder ser implementada e testada. |
| 4 | Cadastro com **aceite LGPD obrigatório** | RNF-003 do PIT I citava a LGPD, mas nenhuma tela pedia consentimento. |
| 5 | Login social (Google/Facebook) removido do MVP | RF-005 do PIT I exige credenciais OAuth externas; não agrega ao objetivo acadêmico. |
| 6 | Pagamento por **gateway simulado** | Integração real exige contrato com adquirente; a simulação reproduz aprovação e recusa e permite testar o fluxo inteiro. |
| 7 | Novo perfil **Entregador** com tela própria | Estava no caso de uso do PIT I, mas sem telas; agora tem painel. |
| 8 | **Formulário de laudo de teste** dentro do app | Atende à Situação 3 (coleta dos 5 laudos com prints). |

## 2. Correções na modelagem UML

| Artefato do PIT I | Problema encontrado | Correção no PIT II |
|---|---|---|
| Diagrama de classes | As 7 classes estavam **sem linhas de relacionamento** (só descritas em texto) | Novo diagrama com associações, composições e multiplicidades: [`classes.png`](../diagramas/classes.png) |
| Diagrama de classes | Faltavam classes para pagamento e rastreamento | Incluídas **Pagamento** e **HistoricoStatus**, e enumerações (StatusPedido, FormaPagamento...) |
| Pedido | `endereco_id` (FK) perdia o histórico se o cliente apagasse o endereço | Pedido guarda **cópia do endereço** (snapshot) |
| Pedido | Status sem regras de transição | **Diagrama de máquina de estados**: [`estados.png`](../diagramas/estados.png) |
| Introdução do PIT I | Citava "diagrama de atividades", mas ele não foi entregue | **Diagrama de atividades** da compra: [`atividades.png`](../diagramas/atividades.png) |
| Arquitetura | "MVC" citado sem diagrama | **Diagrama de arquitetura em camadas**: [`arquitetura.png`](../diagramas/arquitetura.png) |
| Produto | Atributos nutricionais detalhados (carboidratos, proteínas, gorduras) sem uso em nenhuma história | Mantidas só as **calorias**, que aparecem na tela de detalhe |
| ItemPedido | `subtotal` armazenado (dado derivado) | Removido da tabela; calculado (`quantidade × preço_unitário`) → evita inconsistência (3FN) |

Os diagramas originais do PIT I estão preservados em [`docs/diagramas/pit1-original`](../diagramas/pit1-original) para comparação.

## 3. Revisão da IHC

| Item | PIT I | PIT II |
|---|---|---|
| Wireframes | 8 telas (o texto citava 12) | **23 telas implementadas** (ver [`docs/screenshots`](../screenshots)) |
| Mensagens de erro | Não documentadas | Todas as validações têm mensagem clara (ver Manual, seção 6) e há telas 403/404/413/500 |
| Identidade visual | Fundo escuro + rosa `#FF85C0`, cards arredondados | **Mantida** |
| Acessibilidade | Citava WCAG 2.1 | Aplicado: alvos de toque ≥ 44 px, foco visível, `aria-label`, link "pular para o conteúdo", contraste alto, funciona sem JavaScript |
| Navegação | Barra inferior com 5 abas | 4 abas (Início, Carrinho, Pedidos, Conta) - "Categorias" virou chips na própria Home, eliminando um toque |

**Mapa navegacional (implementado):**

```
Início ─┬─ Detalhe do produto ── (+) Carrinho
        ├─ Busca / Categoria
Carrinho ── Cupom ── Checkout (Entrega | Retirada) ── Pagamento (Cartão | PIX) ── Acompanhar pedido
Pedidos ── Acompanhar pedido ── Cancelar
Conta ── Endereços (novo / principal / excluir) ── Sair
Admin: Dashboard ─ Pedidos ─ Pedido (status, entregador) ─ Produtos (CRUD) ─ Cupons ─ Laudos
Entregador: Minhas entregas ── Saí para entrega ── Confirmar entrega
```

## 4. Projeto de dados

- **Conceitual → Lógico:** a partir do diagrama de classes de persistência, cada classe virou uma tabela; composições viraram FKs com `ON DELETE CASCADE`; enumerações viraram colunas com `CHECK`.
- **Normalização (3FN):**
  - 1FN: nenhum atributo multivalorado (a lista `imagens` do PIT I foi substituída por um único campo de cor/ilustração).
  - 2FN: todas as tabelas têm chave simples (`id`), sem dependência parcial.
  - 3FN: removidos atributos derivados (`subtotal` do item); dados de categoria ficam só na tabela `categoria`.
  - Desnormalização **intencional**: `pedido.endereco_entrega` e `item_pedido.preco_unitario` são cópias do momento da compra (registro histórico/fiscal).
- **Físico:** [`database/schema.sql`](../../database/schema.sql) - 10 tabelas, chaves estrangeiras, `CHECK`, `UNIQUE` e índices nas FKs mais consultadas.
- **DER:** [`docs/diagramas/der.png`](../diagramas/der.png)
- **Dicionário de dados:** [`dicionario-de-dados.md`](dicionario-de-dados.md)

**SGBD escolhido: SQLite 3.** É o banco relacional mais instalado do mundo, vem junto com o Python, não exige servidor e o arquivo pode ser versionado/entregue facilmente. O script usa SQL padrão e migra para PostgreSQL/MySQL trocando apenas `AUTOINCREMENT` por `SERIAL`/`AUTO_INCREMENT`.
