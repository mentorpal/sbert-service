# sbert-service

A dockerized REST API service to encode sentences using [sentence-transformers](https://pypi.org/project/sentence-transformers/).

# TODO

 - [ ] scripts to download models
 - [ ] tooling - docker, make
 - [ ] github workflow build
 - [ ] terraform code to deploy to beanstalk
 - [ ] Readme
 - [ ] response caching
 - [ ] detect and use GPU if available
 

## Requirements

- [recommended] [conda](https://www.anaconda.com/) to simplify python version management. 
- python3.8 (must be in path as `python3.8` to build virtualenv)
- make
- [poetry](https://python-poetry.org/docs/) for dependency management

## Testing

First download models once:

```
make download-models
```

To run unit tests:
```
SHARED_ROOT=./shared/installed poetry run coverage run --omit="tests .venv" -m py.test -vv
```



## Licensing

All source code files must include a USC open license header.

To check if files have a license header:

```
make test-license
```

To add license headers:

```
make license
```
