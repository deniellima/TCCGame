## Para executar o projeto no seu computador(com backend), siga os passos abaixo:

1. Clone o repositório do GitHub.

2. pegue a chave de api(package-lock.json), variaveis de ambiente(.env).

3. build container(primeira vez executando ou após mudança no dockerfile):
```bash
docker-compose build
```
ou para contruir o container e subir ao mesmo tempo:
```bash
docker-compose up --build
```

4. subindo o container (toda vez que for executar o projeto):
```bash
docker-compose up
```

3. acessar localhost:8000 e verificar o funcionamento