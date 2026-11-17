# Sweet Dreams Cupcakes

App web de uma loja de cupcakes, feito para o Projeto Integrador Transdisciplinar em Engenharia de Software II (Universidade Positivo).

Aluno: Guilherme Dudu Berti - RGM 48103373

É a continuação do que planejei no PIT I (histórias de usuário, UML e protótipos). O cliente vê o cardápio, monta o carrinho, usa cupom, calcula o frete pelo CEP, paga com cartão ou PIX e acompanha o pedido. Também tem um painel para o administrador e uma tela para o entregador.

![Tela inicial](docs/screenshots/01_home.png)

## Tecnologias

Python 3 com Flask, banco SQLite, HTML/CSS/JavaScript e pytest para os testes. O código segue o padrão MVC.

## Como rodar

Precisa do Python 3.10 ou mais novo (no Windows, marcar "Add Python to PATH" na instalação).

```bash
git clone https://github.com/Guiberti/sweet-dreams-cupcakes.git
cd sweet-dreams-cupcakes
pip install -r requirements.txt
python run.py
```

Depois é só abrir http://localhost:5000. O banco é criado sozinho na primeira vez. O terminal também mostra o endereço para abrir no celular, se estiver no mesmo Wi-Fi.

Para zerar o banco: `flask --app run init-db`

## Usuários de teste

- Cliente: `cliente@teste.com` / `Cliente@123`
- Admin: `admin@sweetdreams.com` / `Admin@123`
- Entregador: `entregador@sweetdreams.com` / `Entrega@123`

## Dados para testar

- Cartão aprovado: `4111 1111 1111 1111`, validade `12/30`, CVV `123`
- Cartão recusado: `4000 0000 0000 0002`
- Cupons: `BEMVINDO10` (10%), `DOCE15` (R$ 15 acima de R$ 80), `EXPIRADO`
- CEP com entrega: `80010-000` (Curitiba) ou `83005-000` (região metropolitana)
- CEP fora da área: `01310-100`
- O cupcake de Nutella está sem estoque, para testar produto esgotado.

O pagamento é simulado: não existe cobrança de verdade.

## Testes

```bash
python -m pytest tests --ignore=tests/e2e -v
```

São 86 testes do servidor (unitários, de integração e de sistema) e mais 20 testes de interface que abrem o navegador. Para rodar os de interface:

```bash
pip install -r requirements-dev.txt
playwright install chromium
python -m pytest tests/e2e -v
```

## Pastas

```
app/          código (models, controllers, services, templates, static)
database/     script do banco e dados iniciais
tests/        testes automatizados
docs/         documentação de cada situação-problema, diagramas, telas e manual
```

## Documentação

- [Manual de uso](docs/manual-de-uso.md)
- [Situação 1 - revisão do planejamento e banco de dados](docs/situacao-1-planejamento/README.md)
- [Situação 2 - desenvolvimento](docs/situacao-2-desenvolvimento/README.md)
- [Situação 3 - testes e validação](docs/situacao-3-testes-validacao/README.md)

## O que ficou para depois

Avaliação de produtos, favoritos, notificações, pagamento real e colocar o site num servidor com HTTPS.
