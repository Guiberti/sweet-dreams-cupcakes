# Dicionário de Dados - Sweet Dreams Cupcakes

SGBD: **SQLite 3** · Script: [`database/schema.sql`](../../database/schema.sql) · Normalização: **3ª Forma Normal**

## usuario

Pessoas que usam o sistema: clientes, administradores e entregadores.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PK, autoincremento | Identificador único do usuário |
| `nome` | VARCHAR(120) | NOT NULL | Nome completo |
| `email` | VARCHAR(160) | NOT NULL; UNIQUE | E-mail de login (único, minúsculo) |
| `senha_hash` | VARCHAR(255) | NOT NULL | Hash PBKDF2/scrypt da senha (nunca a senha pura) |
| `telefone` | VARCHAR(20) | - | Celular com DDD, só dígitos |
| `tipo` | VARCHAR(12) | NOT NULL; DEFAULT 'CLIENTE' | Perfil de acesso: CLIENTE, ADMIN ou ENTREGADOR |
| `ativo` | INTEGER | NOT NULL; DEFAULT 1; CHECK ativo IN (0, 1) | 1 = conta ativa; 0 = bloqueada |
| `data_cadastro` | TIMESTAMP | NOT NULL; DEFAULT CURRENT_TIMESTAMP | Data/hora do cadastro |

## endereco

Endereços de entrega do cliente (0..N por usuário).

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PK, autoincremento | Identificador do endereço |
| `usuario_id` | INTEGER | FK → usuario.id; NOT NULL; ON DELETE CASCADE | Dono do endereço (FK usuario) |
| `apelido` | VARCHAR(40) | NOT NULL; DEFAULT 'Casa' | Rótulo: Casa, Trabalho... |
| `cep` | CHAR(8) | NOT NULL; CHECK length(cep) = 8 | CEP com 8 dígitos |
| `logradouro` | VARCHAR(160) | NOT NULL | Rua/avenida |
| `numero` | VARCHAR(10) | NOT NULL | Número |
| `complemento` | VARCHAR(80) | - | Apto, bloco, referência |
| `bairro` | VARCHAR(80) | NOT NULL | Bairro |
| `cidade` | VARCHAR(80) | NOT NULL | Cidade |
| `uf` | CHAR(2) | NOT NULL | Sigla do estado |
| `principal` | INTEGER | NOT NULL; DEFAULT 0; CHECK principal IN (0, 1) | 1 = endereço padrão do cliente |

## categoria

Agrupamento dos produtos no cardápio.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PK, autoincremento | Identificador |
| `nome` | VARCHAR(60) | NOT NULL; UNIQUE | Nome da categoria (único) |
| `descricao` | VARCHAR(200) | - | Texto de apoio |

## produto

Cupcakes e kits vendidos.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PK, autoincremento | Identificador |
| `categoria_id` | INTEGER | FK → categoria.id; NOT NULL | Categoria (FK categoria) |
| `nome` | VARCHAR(100) | NOT NULL | Nome comercial |
| `descricao` | TEXT | - | Descrição exibida no app |
| `preco` | DECIMAL(10,2) | NOT NULL; CHECK preco > 0 | Preço unitário em R$ (> 0) |
| `estoque` | INTEGER | NOT NULL; DEFAULT 0; CHECK estoque >= 0 | Unidades disponíveis (>= 0) |
| `calorias` | INTEGER | CHECK calorias >= 0 | kcal por unidade |
| `cor` | CHAR(7) | NOT NULL; DEFAULT '#FF85C0' | Cor da cobertura (hex) usada na ilustração |
| `destaque` | VARCHAR(20) | - | Selo: NOVO, PROMOÇÃO... |
| `ativo` | INTEGER | NOT NULL; DEFAULT 1; CHECK ativo IN (0, 1) | 0 = exclusão lógica (some do app, fica no histórico) |
| `data_criacao` | TIMESTAMP | NOT NULL; DEFAULT CURRENT_TIMESTAMP | Data de cadastro |

## cupom

Cupons de desconto.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PK, autoincremento | Identificador |
| `codigo` | VARCHAR(30) | NOT NULL; UNIQUE | Código digitado pelo cliente (único) |
| `tipo_desconto` | VARCHAR(12) | NOT NULL; CHECK tipo_desconto IN ('PERCENTUAL', 'VALOR_FIXO') | PERCENTUAL ou VALOR_FIXO |
| `valor_desconto` | DECIMAL(10,2) | NOT NULL; CHECK valor_desconto > 0 | % ou R$ de desconto |
| `valor_minimo_pedido` | DECIMAL(10,2) | NOT NULL; DEFAULT 0 | Valor mínimo em produtos |
| `data_validade` | DATE | NOT NULL | Último dia de uso |
| `quantidade_disponivel` | INTEGER | NOT NULL; DEFAULT 0; CHECK quantidade_disponivel >= 0 | Usos restantes |
| `ativo` | INTEGER | NOT NULL; DEFAULT 1; CHECK ativo IN (0, 1) | 1 = pode ser usado |

## pedido

Cabeçalho do pedido.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PK, autoincremento | Identificador interno |
| `numero` | VARCHAR(20) | NOT NULL; UNIQUE | Número exibido ao cliente (SD000001) |
| `cliente_id` | INTEGER | FK → usuario.id; NOT NULL | Cliente (FK usuario) |
| `entregador_id` | INTEGER | FK → usuario.id | Entregador atribuído (FK usuario, opcional) |
| `cupom_id` | INTEGER | FK → cupom.id | Cupom usado (FK cupom, opcional) |
| `tipo_entrega` | VARCHAR(10) | NOT NULL; CHECK tipo_entrega IN ('ENTREGA', 'RETIRADA') | ENTREGA ou RETIRADA |
| `endereco_entrega` | VARCHAR(300) | - | Cópia do endereço no momento da compra |
| `status` | VARCHAR(20) | NOT NULL; DEFAULT 'AGUARDANDO_PAGAMENTO' | Situação atual (máquina de estados) |
| `valor_produtos` | DECIMAL(10,2) | NOT NULL | Soma dos itens |
| `valor_frete` | DECIMAL(10,2) | NOT NULL; DEFAULT 0 | Frete cobrado |
| `valor_desconto` | DECIMAL(10,2) | NOT NULL; DEFAULT 0 | Desconto do cupom |
| `valor_total` | DECIMAL(10,2) | NOT NULL | produtos + frete − desconto |
| `observacoes` | VARCHAR(300) | - | Pedido especial do cliente |
| `data_criacao` | TIMESTAMP | NOT NULL; DEFAULT CURRENT_TIMESTAMP | Data/hora do pedido |

## item_pedido

Itens do pedido (composição).

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PK, autoincremento | Identificador |
| `pedido_id` | INTEGER | FK → pedido.id; NOT NULL; ON DELETE CASCADE | Pedido (FK) |
| `produto_id` | INTEGER | FK → produto.id; NOT NULL | Produto (FK) |
| `quantidade` | INTEGER | NOT NULL; CHECK quantidade > 0 | Unidades (> 0) |
| `preco_unitario` | DECIMAL(10,2) | NOT NULL; CHECK preco_unitario > 0 | Preço congelado no momento da compra |

## pagamento

Tentativas de pagamento de um pedido.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PK, autoincremento | Identificador |
| `pedido_id` | INTEGER | FK → pedido.id; NOT NULL; ON DELETE CASCADE | Pedido (FK) |
| `forma` | VARCHAR(10) | NOT NULL; CHECK forma IN ('CARTAO', 'PIX') | CARTAO ou PIX |
| `status` | VARCHAR(10) | NOT NULL; CHECK status IN ('PENDENTE', 'APROVADO', 'RECUSADO') | PENDENTE, APROVADO ou RECUSADO |
| `valor` | DECIMAL(10,2) | NOT NULL | Valor cobrado |
| `cartao_final` | CHAR(4) | - | 4 últimos dígitos (PCI: nunca o número completo) |
| `bandeira` | VARCHAR(20) | - | Visa, Mastercard... |
| `codigo_transacao` | VARCHAR(40) | - | ID devolvido pelo gateway |
| `pix_copia_cola` | VARCHAR(300) | - | Código PIX gerado |
| `motivo_recusa` | VARCHAR(120) | - | Mensagem do emissor |
| `data_criacao` | TIMESTAMP | NOT NULL; DEFAULT CURRENT_TIMESTAMP | Data/hora da tentativa |

## historico_status

Trilha de auditoria de cada mudança de status.

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PK, autoincremento | Identificador |
| `pedido_id` | INTEGER | FK → pedido.id; NOT NULL; ON DELETE CASCADE | Pedido (FK) |
| `status` | VARCHAR(20) | NOT NULL | Novo status |
| `usuario_id` | INTEGER | FK → usuario.id | Quem alterou (FK usuario) |
| `data_hora` | TIMESTAMP | NOT NULL; DEFAULT CURRENT_TIMESTAMP | Quando |

## feedback_teste

Laudos enviados pelos testadores (Situação 3).

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | INTEGER | PK, autoincremento | Identificador |
| `nome_testador` | VARCHAR(120) | NOT NULL | Nome de quem testou |
| `perfil_testador` | VARCHAR(80) | - | Colega, profissional... |
| `data_teste` | DATE | NOT NULL | Data do teste |
| `funcionou` | TEXT | - | O que testou e funcionou |
| `nao_funcionou` | TEXT | - | O que testou e não funcionou |
| `nao_testado` | TEXT | - | O que não testou e por quê |
| `sugestoes` | TEXT | - | Sugestões de melhoria |
| `nota` | INTEGER | CHECK nota BETWEEN 1 AND 5 | Nota de 1 a 5 |
| `print_arquivo` | VARCHAR(200) | - | Nome do arquivo de print enviado |
| `data_envio` | TIMESTAMP | NOT NULL; DEFAULT CURRENT_TIMESTAMP | Data/hora do envio |
