-- =====================================================================
-- Sweet Dreams Cupcakes - Carga inicial (catálogo e cupons)
-- Os usuários de demonstração são criados por app/db.py, pois as senhas
-- precisam ser gravadas com hash (nunca em texto puro).
-- =====================================================================

INSERT INTO categoria (nome, descricao) VALUES
 ('Clássicos', 'Os sabores tradicionais que todo mundo ama'),
 ('Gourmet',   'Receitas autorais com ingredientes premium'),
 ('Veganos',   'Sem ingredientes de origem animal'),
 ('Kits',      'Caixas para presentear e para festas');

INSERT INTO produto (categoria_id, nome, descricao, preco, estoque, calorias, cor, destaque) VALUES
 (1, 'Red Velvet',          'Massa aveludada de cacau com cobertura de cream cheese.',            12.90, 40, 320, '#B0303F', 'MAIS VENDIDO'),
 (1, 'Baunilha Clássico',   'Massa de baunilha de Madagascar e buttercream suave.',              10.90, 35, 290, '#F3E3B0', NULL),
 (1, 'Chocolate Belga',     'Chocolate belga 54% na massa e no ganache.',                         14.90, 30, 350, '#5A3221', NULL),
 (1, 'Morango',             'Massa leve com recheio e cobertura de morango fresco.',              13.50, 25, 300, '#FF7FA0', NULL),
 (2, 'Pistache',            'Massa de pistache com creme de pistache siciliano.',                 18.90, 15, 360, '#9CC27A', 'NOVO'),
 (2, 'Doce de Leite com Flor de Sal', 'Recheio cremoso de doce de leite e toque de flor de sal.', 16.90, 20, 370, '#C98A4B', NULL),
 (2, 'Limão Siciliano',     'Massa cítrica com curd de limão e merengue maçaricado.',             15.90, 18, 310, '#F2E55C', NULL),
 (2, 'Nutella',             'Massa de chocolate recheada com Nutella e avelãs.',                  17.90,  0, 390, '#6B3E26', NULL),
 (3, 'Limão Vegano',        'Sem leite e sem ovos, com cobertura de limão.',                      11.90, 20, 260, '#D8F06A', 'PROMOÇÃO'),
 (3, 'Cacau Vegano',        'Cacau 70% com cobertura de creme de coco.',                          12.90, 20, 280, '#4A2C2A', NULL),
 (4, 'Caixa com 6 sortidos','Seleção do confeiteiro com 6 sabores do dia.',                       69.90, 10, NULL, '#FF85C0', NULL),
 (4, 'Caixa Festa (12 un.)','12 cupcakes para festas e eventos.',                                129.90,  8, NULL, '#E86AA6', NULL);

INSERT INTO cupom (codigo, tipo_desconto, valor_desconto, valor_minimo_pedido, data_validade, quantidade_disponivel) VALUES
 ('BEMVINDO10', 'PERCENTUAL', 10.00,  0.00, '2027-12-31', 500),
 ('DOCE15',     'VALOR_FIXO', 15.00, 80.00, '2027-12-31', 100),
 ('EXPIRADO',   'PERCENTUAL', 20.00,  0.00, '2024-01-01',  50);
