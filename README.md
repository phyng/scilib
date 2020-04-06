
# scilib

[![Github](https://github.com/phyng/scilib/workflows/test/badge.svg)](https://github.com/phyng/scilib/actions) [![Pypi](https://img.shields.io/pypi/v/scilib.svg?style=flat&label=PyPI)](https://pypi.org/project/scilib/)

## documentation

https://phyng.com/scilib/

## install

```bash
# use pip
pip install scilib

# or use poetry
poetry add scilib
```

## test

```bash
npm test
npm test_coverage
```

## usage

### import wos data to ElasticSearch

```bash
env ES_API=http://localhost:9205 python -m scripts.import_to_es --from /path/to/wos_data/ --index wos
```
