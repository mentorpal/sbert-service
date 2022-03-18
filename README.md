# sbert-service

A dockerized REST API service to encode sentences using [sentence-transformers](https://pypi.org/project/sentence-transformers/).

# TODO

 - [ ] terraform code to deploy to beanstalk
 - [ ] nginx ?
 - [ ] sentry
 - [ ] auth&authz!
 - [ ] api quotas
 - [ ] json logging
 - [ ] response caching
 - [ ] detect and use GPU if available
 - [ ] github workflow build
 - [x] benchmark
 - [x] scripts to download models
 - [x] tooling - docker, make
 

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
make test
```

## Load test

First install [k6](https://k6.io/docs/) and then:

```
cd tools && k6 run --vus 10 -i 5000 questions-k6.js
# output:
# default ✓ [======================================] 10 VUs  06m04.3s/10m0s  5000/5000 shared iters
#     http_reqs......................: 5000    13.724361/s
#     http_req_duration..............: avg=727.26ms min=78.93ms med=701.05ms max=1.21s  p(90)=812.63ms p(95)=944.71ms

cd tools && k6 run --vus 20 -i 200 questions-k6.js
# output:
# default ✓ [======================================] 20 VUs  00m15.3s/10m0s  200/200 shared iters
     http_reqs......................: 200     13.070371/s
     http_req_duration..............: avg=1.46s    min=854.79ms med=1.46s max=2.24s  p(90)=1.53s    p(95)=1.55s
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
