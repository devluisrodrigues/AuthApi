# Projeto Cloud - Documentação parte 1

**Autor: Luís Rodrigues**

Link para o Repositório no GitHub: [Repositório](https://github.com/devluisrodrigues/AuthApi)

Link para o Docker Hub: [Docker Hub](https://hub.docker.com/repository/docker/lasr2/authapi)

## **Descrição do Projeto:**

O projeto consiste em uma API RESTful desenvolvida em Python com o framework FastAPI. A API possui três endpoints, um para registrar um novo usuário, a qual adiciona um novo usuário na base de dados. Outro para autenticar um usuário, no qual checa o email e senha do usuário. E um terceiro para consultar uma API externa. A API utiliza um banco de dados PostgreSQL para armazenar os usuários cadastrados.

A API realiza uma consulta, protocolo GET, em uma API externa [JokeAPI](https://publicapis.io/jokes-api) e retorna uma piada sobre programação, no formato, id: int, Pergunta: str, Resposta: str.

Exemplo: curl -X GET "https://official-joke-api.appspot.com/jokes/programming/random"

```json
[
    {
        "id": 15,
        "type": "programming",
        "setup": "What's the best thing about a Boolean?",
        "punchline": "Even if you're wrong, you're only off by a bit."
    }
]
```

O id representa o número da piada catalogada pela API.

Para realizar uma consulta na API é necessário **passar um token JWT** no cabeçalho da requisição, o token é gerado ao registrar ou autenticar um usuário.

## **Configuração do ambiente:**

- Crie um diretório para organizar os arquivos do projeto, por exemplo: `mkdir projeto-cloud`. E acesse o diretório criado: `cd projeto-cloud`

- Crie o `docker-compose.yml` com o seguinte conteúdo:

```yml
services:
  fastapi:
    container_name: fastapi-api
    image: lasr2/authapi:latest
    ports:
      - "8080:8080"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      SECRET_KEY: "${SECRET_KEY:-suaChaveSecreta}"
    restart: always


  db:
    image: postgres:17
    container_name: postgres-database
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-projeto}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-projeto}
      POSTGRES_DB: ${POSTGRES_DB:-projeto}
```

- Crie o arquivo `.env` com o seguinte conteúdo, altere as variáveis de acordo com o seu ambiente:

```env
SECRET_KEY = "chave_secreta_muito_forte"
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
```

- Abra o terminal e execute o comando `docker-compose up -d` para subir os containers

    Caso esteja funcionando corretamente, o terminal exibirá, no final, a mensagem:

```bash
fastapi-api        | INFO:     Started server process [1]
fastapi-api        | INFO:     Waiting for application startup.
fastapi-api        | INFO:     Application startup complete.
fastapi-api        | INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

- Tente acessar o endereço `http://localhost:8080/docs` para verificar se a API está funcionando.

> **Nota Importante:** Perceba que ao utilizar o docker-compose acima, ao utilizar o método docker compose up, o docker irá baixar a imagem do repositório do Docker Hub.

> **Para utilizar novamente:** Depois que o ambiente estiver configurados, basta entrar na pasta do projeto e executar o comando `docker-compose up -d` para subir os containers.

## **Endpoints da API:**

- **Post /registrar**
    <!-- Screenshot da APi rodando -->
    ![API Rodando](./img/registrar.png)
    - Cria um novo usuário
    - Parâmetros:
        - `email`: E-mail do usuário
        - `nome`: Nome do usuário
        - `senha`: Senha do usuário
    - Retorno:
        - `200`: Usuário criado com sucesso, retorna no body da resposta um token JWT
        <!-- EXEMPLO DE BODY DE RESPOSTA -->
        ```json
        {
            "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZTJAZ21haWwiLCJub21lIjoiaHVtYmFzIiwiZXhwIjoxNzI5NzkzNDUzfQ.eKOBfLTVtSZ4wNKjAJ9XugFH8yBZACIlXH2Bvsvt8rY"
        }
        ```
        - `409`: E-mail já cadastrado
    - Exemplo de Chamada:

        ```bash
        curl -X POST "http://localhost:8080/registrar" 
        -H "Content-Type: application/json" 
        -d '{"email": "teste2@gmail", "senha": "123","nome":"humbas"}'
        ```

- **Post /login**
    ![API Rodando](./img/login.png)
    - Autentica um usuário, recebe um e-mail e senha e retorna um token JWT
    - Parâmetros:
        - `email`: E-mail do usuário
        - `senha`: Senha do usuário
    - Retorno:
        - `200`: Usuário autenticado com sucesso, retorna no body da resposta um token JWT
        <!-- EXEMPLO DE BODY DE RESPOSTA -->
        ```json
        {
            "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZTJAZ21haWwiLCJub21lIjoiaHVtYmFzIiwiZXhwIjoxNzI5NzkzNDUzfQ.eKOBfLTVtSZ4wNKjAJ9XugFH8yBZACIlXH2Bvsvt8rY"
        }
        ```
        - `401`: Se o E-mail não estiver cadastrado ou a senha estiver incorreta

    - Exemplo de Chamada:

        ```bash
        curl -X POST "http://localhost:8080/login" -H "Content-Type: application/json" -d '{"email": "teste@gmail", "senha": "123"}'
        ```

- **Get /consultar**
    ![API Rodando](./img/consultar.png)
    - Faz uma consulta em uma API externa, precisa de um token JWT para autenticação
    - Cabeçalho:
        - `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZTNAZ21haWwiLCJub21lIjoiY2FydXNvIiwiZXhwIjoxNzI5ODAyMjgwfQ.ByDfIOOplaGl9akfW2kmk0uQZuXG2f-697pcN5c5-lY`
    - Retorno:
        - `200`: Retorna um JSON com uma pergunta e resposta
        ```json
        {
            "id": 15,
            "Pergunta": "What's the best thing about a Boolean?",
            "Resposta": "Even if you're wrong, you're only off by a bit."
        }
        ```

        - `403`: Token inválido ou expirado

    - Exemplo de Chamada:

        ```bash
        curl -X GET "http://localhost:8080/consultar" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZTNAZ21haWwiLCJub21lIjoiY2FydXNvIiwiZXhwIjoxNzI5ODAyMjgwfQ.ByDfIOOplaGl9akfW2kmk0uQZuXG2f-697pcN5c5-lY"
        ```

> **Nota Importante:** É possível visualizar as informações do JWT contidas em [jwt.io](https://jwt.io/)

## **Vídeo de Demonstração:**

**Link para o vídeo de demonstração: [Vídeo](https://youtu.be/IbsOElNCyss)**