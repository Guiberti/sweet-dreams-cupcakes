# Roteiro do vídeo (5 minutos, narrado)

**Dica de gravação:** use o OBS Studio ou a gravação de tela do Windows (`Win + Alt + R`, Xbox Game Bar) ou do PowerPoint (*Inserir → Gravação de Tela*). Deixe o app aberto em `http://localhost:5000` com o DevTools em modo celular (F12 → ícone de celular) ou espelhe o celular. Rode `flask --app run init-db` antes, para o banco começar limpo.

| Tempo | O que mostrar na tela | O que falar (sugestão) |
|---|---|---|
| 0:00–0:30 | GitHub do projeto (README) | "Olá, sou o Guilherme Dudu Berti, RGM 48103373. Este é o Sweet Dreams Cupcakes, o app de e-commerce de cupcakes que planejei no Projeto Integrador I e agora implementei no II, em Python com Flask, padrão MVC e banco SQLite." |
| 0:30–1:00 | Pastas `app/models`, `controllers`, `templates`, `services` e `database/schema.sql` | "O código segue o MVC: os models acessam o banco, os controllers recebem as requisições e as views são as páginas HTML. As regras de frete, pagamento e validação ficam em services, separadas para poderem ser testadas." |
| 1:00–1:30 | Home → busca "pistache" → chip "Veganos" → detalhe | "Na vitrine o cliente busca, filtra por categoria e vê os detalhes: calorias e estoque. Produto esgotado fica cinza e não pode ser comprado." |
| 1:30–2:15 | Adicionar 2 itens → carrinho → cupom `EXPIRADO` (erro) → `BEMVINDO10` | "O carrinho controla o estoque. O cupom é validado: aqui, um expirado mostra o motivo; o BEMVINDO10 aplica 10%." |
| 2:15–3:15 | Checkout → endereço → frete → pagamento com cartão recusado → aprovado | "No checkout o frete é calculado pelo CEP - Curitiba, região metropolitana ou retirada. O pedido é gravado numa transação que baixa o estoque. Primeiro um cartão recusado, com a mensagem de erro tratada; depois um aprovado. O sistema guarda só os 4 últimos dígitos do cartão." |
| 3:15–3:45 | Login admin → dashboard → pedido → Em preparo → atribuir entregador | "O administrador vê o faturamento, muda o status - só as transições permitidas aparecem - e atribui o entregador." |
| 3:45–4:10 | Login entregador → Saí para entrega → Confirmar | "O entregador vê as entregas dele e confirma. O cliente acompanha tudo pela linha do tempo." |
| 4:10–4:40 | Terminal: `python -m pytest -v` (83 passed) | "Fiz 83 testes automatizados com pytest: unitários, de integração e de sistema, todos passando. Eles acharam um bug real no pagamento, que corrigi." |
| 4:40–5:00 | Admin → Laudos de teste | "Cinco pessoas testaram pelo formulário do próprio app. As sugestões adotadas foram: [citar 1 ou 2]. Obrigado!" |

**Checklist antes de enviar:** áudio audível · duração ≈ 5 min · link do vídeo (YouTube não listado ou Google Drive com acesso a "qualquer pessoa com o link") colocado no README e na atividade.
