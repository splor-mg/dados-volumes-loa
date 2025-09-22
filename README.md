# volumes-loa-dados

[![Updated](https://github.com/splor-mg/volumes-loa-dados/actions/workflows/all.yaml/badge.svg)](https://github.com/splor-mg/volumes-loa-dados/actions/)

## Pré-requisitos


1. Criar e ativar ambiente virtual do python 3.10

2. Instalar pacotes Python:

```
pip install -r requirements.txt
```

4. Instalar pacotes R:
```R
Rscript -e 'renv::install(library= "<caminho/para/library/de/sistema/do/R>")'
```

Obs.: Para listar o caminho das libraries do R, utilize 
```
Rscript -e '.libPaths()'
```

## Uso

```bash
make all
```

