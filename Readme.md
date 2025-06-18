# Doc Sumarizer

Aplicação que tem como função sumarizar os documentos 
selecionando suas palavras chaves, instituições
e demais informações referemtes ao documento

## Inicialização

### Terminal

Para iniciar a aplicação pelo terminal utilize o 
seguinte comando:

#### Instalação:

Para a primeira vez executando a aplicação,
rode os comandos no terminal:

```
pip install --no-cache-dir -r requirements.txt
```

```
RUN python -m spacy download pt_core_news_sm
```

Para rodar a aplicação no terminal local execute
o comando a seguir no terminal

```
uvicorn main:app --reload
```

### Rodando com docker

Com o docker instalado, rode o seguinte comando
para executar a imagem

```
docker-compose up --build
```

Para encerrar o container docker precione
```Ctrl + C``` no terminal e execute o seguinte
comando:

```
docker-compose down
```