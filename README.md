## Para executar o projeto no seu computador, siga os passos abaixo:

1. Clone o repositório do GitHub(caso não tenha).

2. Inicialize um ambiente virtual (opcional):
```bash
python -m venv <nome_do_ambiente>
```

```bash
<nome_do_ambiente>/Scripts/Activate
```

3. Instale as dependências necessárias:
```bash
pip install -r requirements.txt
```
4. Execute o django para a aplicação web:
```bash
python manage.py runserver
```

## Usando container docker

1. build container:
```bash
docker compose build
```

2. up container:
```bash
docker compose up
```