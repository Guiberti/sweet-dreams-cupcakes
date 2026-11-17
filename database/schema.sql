-- =====================================================================
-- Sweet Dreams Cupcakes - Projeto Físico do Banco de Dados
-- SGBD: SQLite 3 (portável para PostgreSQL/MySQL com ajustes mínimos)
-- Modelo normalizado até a 3ª Forma Normal (3FN)
-- =====================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS feedback_teste;
DROP TABLE IF EXISTS historico_status;
DROP TABLE IF EXISTS pagamento;
DROP TABLE IF EXISTS item_pedido;
DROP TABLE IF EXISTS pedido;
DROP TABLE IF EXISTS cupom;
DROP TABLE IF EXISTS produto;
DROP TABLE IF EXISTS categoria;
DROP TABLE IF EXISTS endereco;
DROP TABLE IF EXISTS usuario;

-- ---------------------------------------------------------------------
-- USUARIO: clientes, administradores e entregadores (generalização por tipo)
-- ---------------------------------------------------------------------
CREATE TABLE usuario (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nome           VARCHAR(120) NOT NULL,
    email          VARCHAR(160) NOT NULL UNIQUE,
    senha_hash     VARCHAR(255) NOT NULL,
    telefone       VARCHAR(20),
    tipo           VARCHAR(12)  NOT NULL DEFAULT 'CLIENTE'
                   CHECK (tipo IN ('CLIENTE', 'ADMIN', 'ENTREGADOR')),
    ativo          INTEGER      NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    data_cadastro  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- ENDERECO: um usuário possui 0..N endereços
-- ---------------------------------------------------------------------
CREATE TABLE endereco (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id   INTEGER      NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    apelido      VARCHAR(40)  NOT NULL DEFAULT 'Casa',
    cep          CHAR(8)      NOT NULL CHECK (length(cep) = 8),
    logradouro   VARCHAR(160) NOT NULL,
    numero       VARCHAR(10)  NOT NULL,
    complemento  VARCHAR(80),
    bairro       VARCHAR(80)  NOT NULL,
    cidade       VARCHAR(80)  NOT NULL,
    uf           CHAR(2)      NOT NULL,
    principal    INTEGER      NOT NULL DEFAULT 0 CHECK (principal IN (0, 1))
);
CREATE INDEX idx_endereco_usuario ON endereco(usuario_id);

-- ---------------------------------------------------------------------
-- CATEGORIA e PRODUTO: um produto pertence a exatamente uma categoria
-- ---------------------------------------------------------------------
CREATE TABLE categoria (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       VARCHAR(60)  NOT NULL UNIQUE,
    descricao  VARCHAR(200)
);

CREATE TABLE produto (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria_id  INTEGER       NOT NULL REFERENCES categoria(id),
    nome          VARCHAR(100)  NOT NULL,
    descricao     TEXT,
    preco         DECIMAL(10,2) NOT NULL CHECK (preco > 0),
    estoque       INTEGER       NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    calorias      INTEGER       CHECK (calorias >= 0),
    cor           CHAR(7)       NOT NULL DEFAULT '#FF85C0',
    destaque      VARCHAR(20),
    ativo         INTEGER       NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    data_criacao  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_produto_categoria ON produto(categoria_id);

-- ---------------------------------------------------------------------
-- CUPOM de desconto
-- ---------------------------------------------------------------------
CREATE TABLE cupom (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo                 VARCHAR(30)   NOT NULL UNIQUE,
    tipo_desconto          VARCHAR(12)   NOT NULL CHECK (tipo_desconto IN ('PERCENTUAL', 'VALOR_FIXO')),
    valor_desconto         DECIMAL(10,2) NOT NULL CHECK (valor_desconto > 0),
    valor_minimo_pedido    DECIMAL(10,2) NOT NULL DEFAULT 0,
    data_validade          DATE          NOT NULL,
    quantidade_disponivel  INTEGER       NOT NULL DEFAULT 0 CHECK (quantidade_disponivel >= 0),
    ativo                  INTEGER       NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

-- ---------------------------------------------------------------------
-- PEDIDO: cabeçalho. Endereço é copiado (snapshot) para preservar o
-- histórico mesmo que o cliente altere/exclua o endereço depois.
-- ---------------------------------------------------------------------
CREATE TABLE pedido (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    numero            VARCHAR(20)   NOT NULL UNIQUE,
    cliente_id        INTEGER       NOT NULL REFERENCES usuario(id),
    entregador_id     INTEGER       REFERENCES usuario(id),
    cupom_id          INTEGER       REFERENCES cupom(id),
    tipo_entrega      VARCHAR(10)   NOT NULL CHECK (tipo_entrega IN ('ENTREGA', 'RETIRADA')),
    endereco_entrega  VARCHAR(300),
    status            VARCHAR(20)   NOT NULL DEFAULT 'AGUARDANDO_PAGAMENTO'
                      CHECK (status IN ('AGUARDANDO_PAGAMENTO', 'CONFIRMADO', 'EM_PREPARO',
                                        'SAIU_PARA_ENTREGA', 'ENTREGUE', 'CANCELADO')),
    valor_produtos    DECIMAL(10,2) NOT NULL,
    valor_frete       DECIMAL(10,2) NOT NULL DEFAULT 0,
    valor_desconto    DECIMAL(10,2) NOT NULL DEFAULT 0,
    valor_total       DECIMAL(10,2) NOT NULL,
    observacoes       VARCHAR(300),
    data_criacao      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_pedido_cliente    ON pedido(cliente_id);
CREATE INDEX idx_pedido_entregador ON pedido(entregador_id);
CREATE INDEX idx_pedido_status     ON pedido(status);

-- ---------------------------------------------------------------------
-- ITEM_PEDIDO: composição com PEDIDO; preço unitário congelado na compra
-- ---------------------------------------------------------------------
CREATE TABLE item_pedido (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id       INTEGER       NOT NULL REFERENCES pedido(id) ON DELETE CASCADE,
    produto_id      INTEGER       NOT NULL REFERENCES produto(id),
    quantidade      INTEGER       NOT NULL CHECK (quantidade > 0),
    preco_unitario  DECIMAL(10,2) NOT NULL CHECK (preco_unitario > 0),
    UNIQUE (pedido_id, produto_id)
);

-- ---------------------------------------------------------------------
-- PAGAMENTO: 1 pedido possui 1..N tentativas de pagamento.
-- Nunca armazenamos o número completo do cartão (PCI-DSS): só os 4 finais.
-- ---------------------------------------------------------------------
CREATE TABLE pagamento (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id       INTEGER       NOT NULL REFERENCES pedido(id) ON DELETE CASCADE,
    forma           VARCHAR(10)   NOT NULL CHECK (forma IN ('CARTAO', 'PIX')),
    status          VARCHAR(10)   NOT NULL CHECK (status IN ('PENDENTE', 'APROVADO', 'RECUSADO')),
    valor           DECIMAL(10,2) NOT NULL,
    cartao_final    CHAR(4),
    bandeira        VARCHAR(20),
    codigo_transacao VARCHAR(40),
    pix_copia_cola  VARCHAR(300),
    motivo_recusa   VARCHAR(120),
    data_criacao    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_pagamento_pedido ON pagamento(pedido_id);

-- ---------------------------------------------------------------------
-- HISTORICO_STATUS: trilha de auditoria para o rastreamento do pedido
-- ---------------------------------------------------------------------
CREATE TABLE historico_status (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id    INTEGER     NOT NULL REFERENCES pedido(id) ON DELETE CASCADE,
    status       VARCHAR(20) NOT NULL,
    usuario_id   INTEGER     REFERENCES usuario(id),
    data_hora    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_historico_pedido ON historico_status(pedido_id);

-- ---------------------------------------------------------------------
-- FEEDBACK_TESTE: laudos dos testadores (Situação-Problema 3)
-- ---------------------------------------------------------------------
CREATE TABLE feedback_teste (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_testador      VARCHAR(120) NOT NULL,
    perfil_testador    VARCHAR(80),
    data_teste         DATE         NOT NULL,
    funcionou          TEXT,
    nao_funcionou      TEXT,
    nao_testado        TEXT,
    sugestoes          TEXT,
    nota               INTEGER      CHECK (nota BETWEEN 1 AND 5),
    print_arquivo      VARCHAR(200),
    data_envio         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
