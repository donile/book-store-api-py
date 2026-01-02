# FastAPI Example

## Start API

```sh
$ fastapi dev src/app/main.py
```

## Run Tests

```sh
$ pytest
```

## Build Container
```sh
$ docker build -t fast-api-example .
```

## Start Container
```sh
$ docker run --name fast-api-example -p 8000:80 fast-api-example
```

## Start MongoDB Container
```sh
$ docker run --name mongo-fast-api-example --restart=always -p 29017:27017 -d mongo:8.2.2-noble
```



# To Do
- How to configure FastAPI?
- Logging?