# volumes-loa-dados

[![Updated](https://github.com/splor-mg/volumes-loa-dados/actions/workflows/all.yaml/badge.svg)](https://github.com/splor-mg/volumes-loa-dados/actions/)

## Pré-requisitos

Esse projeto utiliza Docker para gerenciamento das dependências. Para fazer _build_  da imagem execute:

```bash
docker build --tag volumes-loa-dados .
```

## Uso

Para executar o container

```bash
docker run -it --rm --mount type=bind,source=$(PWD),target=/project volumes-loa-dados bash
```

Uma vez dentro do container execute os comandos do make

```bash
make all
```

_Gerado a partir de [cookiecutter-datapackage@a6842ad](https://github.com/splor-mg/cookiecutter-datapackage/commit/a6842adfcb272c31087ae2c891df3637dd5f0dee)_
