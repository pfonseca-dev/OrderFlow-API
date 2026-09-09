<div align="center">

# OrderFlow API

### Gerenciamento inteligente de pedidos e entregas

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-465876?style=flat-square)](https://alembic.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)](https://docs.pytest.org/)

</div>

> API REST para gerenciamento de produtos e pedidos, com cálculo de entrega e controle do ciclo de status.

💡 **Documentação da API:** <http://localhost:8000/docs> — disponível com a aplicação em execução.

### Navegação

| Projeto | Execução | Referência |
| --- | --- | --- |
| [Sobre o projeto](#sobre-o-projeto) | [Pré-requisitos](#pré-requisitos) | [API](#api) |
| [Funcionalidades](#funcionalidades) | [Configuração](#configuração) | [Ciclo de status](#ciclo-de-status) |
| [Arquitetura](#arquitetura) | [Docker](#execução-com-docker) | [Cálculo de entrega](#cálculo-de-entrega) |
| [Tecnologias](#tecnologias) | [Execução local](#execução-local) | [Migrations](#migrations) |
| [Estrutura do repositório](#estrutura-do-repositório) | [Testes e qualidade](#testes-e-qualidade) | [Solução de problemas](#solução-de-problemas) |

## Sobre o projeto

Desenvolvido com **FastAPI e PostgreSQL**, o OrderFlow API organiza o fluxo de pedidos em camadas, separando contratos HTTP, regras de negócio e acesso aos dados.

Cada pedido preserva o preço unitário dos produtos no momento da criação e reúne itens, valores de entrega e status para consulta.

## Funcionalidades

- Cadastro, listagem e consulta de produtos por ID.
- Criação de pedidos com múltiplos itens e validação de produtos existentes e disponíveis.
- Cálculo automático dos subtotais dos itens, subtotal do pedido e total.
- Cálculo de distância por Haversine e taxa de entrega por faixa de distância.
- Listagem e consulta de pedidos por ID.
- Atualização de status com validação das transições permitidas.
- Persistência em PostgreSQL com migrations Alembic.

## Arquitetura

```text
           Cliente HTTP / Swagger
                     |
                     v
              FastAPI / Rotas
              Schemas Pydantic
                     |
                     v
       ProductService / OrderService
                     |       |
                     |       +--> DeliveryService
                     |            (distância e taxa)
                     v
                Repositories
                     |
                     v
             SQLAlchemy / Session
                     |
                     v
                PostgreSQL
```

As rotas recebem e validam os dados pelos schemas. Os serviços aplicam as regras de negócio; os repositórios consultam e persistem os modelos ORM.

O `OrderService` usa o `DeliveryService` para calcular a entrega.

## Tecnologias

| Tecnologia | Papel no projeto |
| --- | --- |
| Python 3.12+ | Linguagem; o Dockerfile utiliza Python 3.12 |
| FastAPI e Uvicorn | API HTTP, documentação interativa e servidor ASGI |
| Pydantic e pydantic-settings | Validação de dados e configuração por ambiente |
| PostgreSQL 16 | Banco relacional; versão utilizada no Compose |
| SQLAlchemy e Psycopg | ORM, sessões e conexão com PostgreSQL |
| Alembic | Versionamento do schema do banco |
| Docker e Docker Compose | Execução da API e do banco em containers |
| Pytest, Ruff e mypy | Testes, lint, formatação e análise de tipos |

As dependências estão fixadas em [requirements.txt](requirements.txt), e as ferramentas são configuradas em [pyproject.toml](pyproject.toml).

## Pré-requisitos

- **Docker:** Docker Engine e plugin Docker Compose, com as portas `8000` e `5433` livres no host.
- **Execução local:** Python 3.12+, `pip` e PostgreSQL acessível. O banco pode ser iniciado pelo Compose.
- **Atalhos de desenvolvimento:** `make`, caso queira usar o Makefile.

## Configuração

Para execução local, copie o exemplo na raiz do projeto, caso ainda não tenha um `.env`:

```bash
cp .env.example .env
```

| Variável | Valor no exemplo | Uso |
| --- | --- | --- |
| `APP_NAME` | `OrderFlow API` | Título da API e mensagem da rota `/` |
| `PORT` | `8000` | Carregada nas configurações; os comandos atuais do Uvicorn fixam `--port 8000` |
| `DATABASE_URL` | `postgresql+psycopg://orderflow:orderflow@localhost:5432/orderflow` | Conexão com o banco; obrigatória |
| `RESTAURANT_LATITUDE` | `-23.550520` | Latitude de origem da entrega; obrigatória |
| `RESTAURANT_LONGITUDE` | `-46.633308` | Longitude de origem da entrega; obrigatória |

A aplicação aceita variáveis do ambiente ou do `.env`.

> **Configuração no Docker:** no Compose, os valores são definidos diretamente em `services.api.environment`. Esse fluxo dispensa o `.env`, e alterações nele não substituem os valores definidos no Compose.

## Execução com Docker

### Iniciar os serviços

Na raiz do repositório:

```bash
docker compose up --build
```

O Compose inicia o PostgreSQL, aguarda seu health check e executa `alembic upgrade head` antes de iniciar a API com Uvicorn.

| Serviço | Container | Acesso pelo host |
| --- | --- | --- |
| `api` | `orderflow-api` | <http://localhost:8000> |
| `db` | `orderflow-db` | `localhost:5433` → porta `5432` do container |

A API conecta-se ao banco pela rede interna em `db:5432`. Os dados ficam no volume `orderflow_postgres_data`.

### Acompanhar e encerrar

```bash
docker compose ps              # Consultar os serviços
docker compose logs -f api     # Acompanhar os logs da API
docker compose down            # Encerrar, preservando o volume do banco
```

> **Remoção dos dados:** para descartar também os dados do banco, use `docker compose down -v`.

## Execução local

### 1. Preparar o ambiente

Crie e ative o ambiente virtual:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar o banco

Prepare o `.env` conforme [Configuração](#configuração). O banco e o usuário informados na conexão precisam existir.

| Local do banco | Endereço na `DATABASE_URL` da API local |
| --- | --- |
| PostgreSQL no host, na porta padrão | `localhost:5432` (como no `.env.example`) |
| PostgreSQL do Compose | `localhost:5433` |

Para usar o banco do Compose, execute `docker compose up -d db` e ajuste no `.env`:

```dotenv
DATABASE_URL="postgresql+psycopg://orderflow:orderflow@localhost:5433/orderflow"
```

### 3. Aplicar migrations e iniciar a API

```bash
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Atalhos:** `make migrate` e `make dev`. A porta `8000` deve estar livre para a API local.

## API

**[Swagger UI](http://localhost:8000/docs)** · **[ReDoc](http://localhost:8000/redoc)** · **[OpenAPI JSON](http://localhost:8000/openapi.json)**

### Endpoints

| Método | Endpoint | Operação |
| --- | --- | --- |
| `GET` | `/` | Mensagem com o nome da aplicação |
| `GET` | `/api/health` | Retorna `{"status":"ok"}`; não consulta o banco |
| `POST` | `/api/products` | Cadastrar produto |
| `GET` | `/api/products` | Listar produtos |
| `GET` | `/api/products/{product_id}` | Consultar produto |
| `POST` | `/api/orders` | Criar pedido com itens e destino |
| `GET` | `/api/orders` | Listar pedidos |
| `GET` | `/api/orders/{order_id}` | Consultar pedido |
| `PATCH` | `/api/orders/{order_id}/status` | Atualizar status e retornar o pedido completo |

**Respostas HTTP:** as criações retornam `201`; as consultas e a atualização de status, `200`.

Erros de validação retornam `422`, recursos inexistentes retornam `404`, e produto indisponível ou transição de status inválida retornam `400`.

### Exemplo de fluxo

**1. Cadastrar um produto**

```bash
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Hambúrguer Clássico","description":"Pão, carne e queijo","price":"29.90","is_available":true}'
```

`name`, `description` e `price` são obrigatórios; `description` aceita `null`. O preço deve ser positivo, com até 10 dígitos e 2 casas decimais. A disponibilidade assume `true` quando omitida.

**2. Criar um pedido**

Use o ID do produto retornado no lugar de `1`:

```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{"product_id":1,"quantity":2}],
    "delivery": {"latitude":"-23.550520","longitude":"-46.633308"}
  }'
```

O pedido exige pelo menos um item e as coordenadas de entrega. `product_id` deve ser positivo; `quantity` aceita inteiros de `1` a `2147483647`. Latitude e longitude devem estar, respectivamente, entre `-90` e `90` e entre `-180` e `180`.

A resposta inclui `id`, `status`, `items`, `subtotal`, `delivery_distance_km`, `delivery_fee` e `total`. Cada item traz `product_id`, `quantity`, `unit_price` e `subtotal`.

**3. Consultar e confirmar o pedido**

Substitua `1` pelo ID do pedido retornado:

```bash
curl http://localhost:8000/api/orders/1

curl -X PATCH http://localhost:8000/api/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"confirmed"}'
```

## Ciclo de status

Todo pedido começa em `pending`:

```text
pending --> confirmed --> preparing --> out_of_delivery --> delivered
   |            |             |
   +------------+-------------+--> cancelled
```

**Estados finais:** `delivered` e `cancelled`.

O cancelamento é permitido em `pending`, `confirmed` e `preparing`. Transições fora desse fluxo, inclusive repetir o status atual, retornam `400`.

## Cálculo de entrega

O `DeliveryService` aplica Haversine às coordenadas do restaurante e do destino para obter a distância em quilômetros. A distância é arredondada para duas casas decimais com `ROUND_HALF_UP` antes de definir a taxa.

| Distância calculada | Taxa de entrega |
| --- | --- |
| Até 2,00 km | 5,00 |
| Acima de 2,00 até 5,00 km | 8,00 |
| Acima de 5,00 até 10,00 km | 12,00 |
| Acima de 10,00 km | 18,00 |

```text
subtotal do item = preço unitário armazenado × quantidade
subtotal do pedido = soma dos subtotais dos itens
total = subtotal do pedido + taxa de entrega
```

Preço unitário, coordenadas, distância e taxa são persistidos. Subtotal e total são calculados ao montar a resposta do pedido.

## Migrations

O histórico em `migrations/versions/` cria as tabelas `orders`, `products` e `order_items` e adiciona os campos de entrega.

Com o ambiente local configurado:

```bash
alembic upgrade head                                      # Aplicar migrations
alembic current                                           # Consultar revisão atual
alembic revision --autogenerate -m "descricao_da_alteracao" # Gerar migration
```

> **Revisão:** revise migrations geradas antes de aplicá-las. No Compose, a aplicação das migrations já faz parte da inicialização da API.

## Testes e qualidade

A suíte Pytest verifica produtos, pedidos com múltiplos itens, valores calculados, validações de entrada, entrega, transições de status e health check. Há testes de modelos e serviços, além dos testes HTTP com `TestClient`.

> **Banco de testes:** os testes HTTP usam o banco configurado e gravam dados sem rollback ou limpeza automática.

Configure um PostgreSQL dedicado ou descartável em `DATABASE_URL`, informe as coordenadas obrigatórias e aplique as migrations antes da suíte.

```bash
alembic upgrade head
pytest -v
ruff check .
ruff format --check .
mypy app
```

**Atalhos:** `make test`, `make lint` e `make typecheck`.

Para aplicar formatação e correções automáticas de lint, use `make format`.

## Estrutura do repositório

```text
.
├── app/
│   ├── main.py          # Aplicação FastAPI e registro das rotas
│   ├── api/             # Router principal e endpoints
│   ├── core/            # Configurações de ambiente
│   ├── database/        # Engine, sessões e dependência de banco
│   ├── models/          # Product, Order e OrderItem
│   ├── repositories/    # Consultas e persistência
│   ├── schemas/         # Contratos Pydantic
│   └── services/        # Produtos, pedidos e cálculo de entrega
├── migrations/          # Configuração e revisões Alembic
├── tests/               # Testes automatizados
├── .env.example         # Exemplo de configuração local
├── Dockerfile           # Imagem da API
├── docker-compose.yaml  # Serviços API e PostgreSQL
├── alembic.ini          # Configuração do Alembic
├── Makefile             # Atalhos de desenvolvimento
├── pyproject.toml       # Metadados e configuração das ferramentas
├── requirements.txt     # Dependências fixadas
└── README.md
```

## Solução de problemas

| Sintoma | O que verificar |
| --- | --- |
| Erro de configuração ao iniciar | Defina `DATABASE_URL`, `RESTAURANT_LATITUDE` e `RESTAURANT_LONGITUDE`; na execução local, use o `.env` na raiz. |
| Conexão recusada com PostgreSQL | Confira credenciais e serviço ativo. Use `db:5432` dentro do Compose e `localhost:5433` para acessar esse banco pelo host. |
| Porta já em uso | Confira processos ou containers nas portas `8000` e `5433`; encerre a instância conflitante ou ajuste o mapeamento no Compose. |
| Tabela ou coluna inexistente | Execute `alembic upgrade head` no banco configurado. No Compose, consulte `docker compose logs api`. |
| API não inicia no Compose | Consulte `docker compose ps` e `docker compose logs db api` para verificar o health check do banco e a execução das migrations. |
| Alterações no `.env` não afetam o Compose | Ajuste os valores definidos diretamente em `services.api.environment` no `docker-compose.yaml` e recrie o serviço. |

## Estado atual

O escopo implementado reúne catálogo, pedidos, cálculo de entrega e controle de status, com persistência e testes automatizados.

As listagens retornam todos os registros; as rotas de produtos permitem criação e consulta, e a atualização de pedidos ocorre pelo status.

## Autor

**Pedro Fonseca Martins**
