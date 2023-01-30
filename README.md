# sbert-service

A dockerized REST API service to encode sentences using [sentence-transformers](https://pypi.org/project/sentence-transformers/).

# TODO

 - [ ] json logging
 - [ ] cicd pipeline
 - [ ] https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/restrict-access-to-load-balancer.html
 - [ ] swagger
 - [ ] CloudFront respond with json on errors:
 < HTTP/2 403
< content-type: text/html
< x-cache: Error from cloudfront
<
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<HTML><HEAD><META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
<TITLE>ERROR: The request could not be satisfied</TITLE>
...
 - [ ] WONT DO: detect and use GPU if available
 - [ ] WONT DO: nginx (beanstalk has a built-in one)
 - [x] response caching (CloudFront)
 - [x] auth&authz!
 - [x] measure response time
 - [x] error handlers
 - [x] sentry
 - [x] terraform code to deploy to beanstalk
 - [x] benchmark
 - [x] scripts to download models
 - [x] tooling - docker, make
 

## Requirements

- [recommended] [conda](https://www.anaconda.com/) to simplify python version management. 
-  python3.10(must be in path as `python3.10` to build virtualenv)
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

To invoke the API manually (qa is the stage):

```bash
curl -H "Authorization: Bearer secret_key" https://sbert-qa.mentorpal.org/v1/encode\?query\=hello+world

curl -H "Authorization: Bearer secret_key" -H 'Content-type: application/json' https://sbert-qa.mentorpal.org/v1/encode/cos_sim_weight --data-raw '{"a":["hello world"],"b":["hi world"]}'
```


## Deployment

To provision the infrastructure use terragrunt and terrafrom and apply `sbert-service`.

To use ECR instead of dockerhub, apply the shared/ecr module. To get login credentials
go to the AWS console, open the sbert_service repository (e.g.
https://us-east-1.console.aws.amazon.com/ecr/repositories/private/<account_id>/sbert_service?region=us-east-1),
then click on the "View push commands", it will explain how to login, tag and push. 

Use `make docker-build` to build the image, then tag and push. Update the ebs/bundle/Dockerrun.aws.json to
point to the tagged image, and then run `make deploy.zip`. After that go to the beanstalk console and upload the zip. 

## Load test

First install [k6](https://k6.io/docs/) and then:

```
cd tools && API_KEY=<redacted> k6 run --vus 10 -i 5000 encode-k6.js
# before CloudFront:
# default ✓ [======================================] 10 VUs  06m04.3s/10m0s  5000/5000 shared iters
#     http_reqs......................: 5000    13.724361/s
#     http_req_duration..............: avg=727.26ms min=78.93ms med=701.05ms max=1.21s  p(90)=812.63ms p(95)=944.71ms
#
# with CloudFront:
default ✓ [======================================] 10 VUs  02m07.7s/10m0s  5000/5000 shared iters
#     http_reqs......................: 5000    39.147187/s
#     http_req_duration..............: avg=254.12ms min=22.85ms med=300.96ms max=805.31ms p(90)=455.77ms p(95)=495.56ms

cd tools && API_KEY=<redacted> k6 run --vus 20 -i 200 encode-k6.js
# before CloudFront:
# default ✓ [======================================] 20 VUs  00m15.3s/10m0s  200/200 shared iters
     http_reqs......................: 200     13.070371/s
     http_req_duration..............: avg=1.46s    min=854.79ms med=1.46s max=2.24s  p(90)=1.53s    p(95)=1.55s
# with CloudFront:
     http_reqs......................: 200     23.436861/s
     http_req_duration..............: avg=697.5ms  min=159.38ms med=731.63ms max=964.7ms  p(90)=873.5ms  p(95)=910.62ms
```

Testing auto-scaling:

```
$ API_KEY=<redacted> k6 run --vus 40 --duration 5m ./encode-k6.js

          /\      |‾‾| /‾‾/   /‾‾/
     /\  /  \     |  |/  /   /  /
    /  \/    \    |     (   /   ‾‾\
   /          \   |  |\  \ |  (‾)  |
  / __________ \  |__| \__\ \_____/ .io

  execution: local
     script: ./encode-k6.js
     output: -

  scenarios: (100.00%) 1 scenario, 40 max VUs, 5m30s max duration (incl. graceful stop):
           * default: 40 looping VUs for 5m0s (gracefulStop: 30s)


running (5m01.3s), 00/40 VUs, 14610 complete and 0 interrupted iterations
default ✓ [======================================] 40 VUs  5m0s

     ✓ is status 200
     ✓ has no errors

     checks.........................: 100.00% ✓ 29220     ✗ 0
     data_received..................: 228 MB  756 kB/s
     data_sent......................: 3.0 MB  9.9 kB/s
     http_req_blocked...............: avg=1.9ms    min=0s       med=0s       max=709.97ms p(90)=1µs   p(95)=1µs
     http_req_connecting............: avg=384.89µs min=0s       med=0s       max=141.46ms p(90)=0s    p(95)=0s
     http_req_duration..............: avg=820.57ms min=172.47ms med=799.06ms max=3.88s    p(90)=1.39s p(95)=1.5s
       { expected_response:true }...: avg=820.57ms min=172.47ms med=799.06ms max=3.88s    p(90)=1.39s p(95)=1.5s
     http_req_failed................: 0.00%   ✓ 0         ✗ 14610
     http_req_receiving.............: avg=641.36µs min=58µs     med=148µs    max=202.78ms p(90)=269µs p(95)=444.54µs
     http_req_sending...............: avg=67.43µs  min=24µs     med=64µs     max=5.14ms   p(90)=90µs  p(95)=108µs
     http_req_tls_handshaking.......: avg=1.38ms   min=0s       med=0s       max=518.67ms p(90)=0s    p(95)=0s
     http_req_waiting...............: avg=819.86ms min=172.13ms med=797.96ms max=3.88s    p(90)=1.39s p(95)=1.5s
     http_reqs......................: 14610   48.490198/s
     iteration_duration.............: avg=822.79ms min=173.15ms med=802.84ms max=3.88s    p(90)=1.4s  p(95)=1.5s
     iterations.....................: 14610   48.490198/s
     vus............................: 7       min=7       max=40
     vus_max........................: 40      min=40      max=40
```

# Known Issues

- The (beanstalk module)[https://github.com/cloudposse/terraform-aws-elastic-beanstalk-environment] does not allow to specify desired instances count for autoscaling and it seems to be max by default.
- The (beanstalk module)[https://github.com/cloudposse/terraform-aws-elastic-beanstalk-environment] does not allow to specify desired duration period for autoscaling and it's 5min by default (would be better to be more aggresive)


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

# Resources

 - https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create_deploy_docker_v2config.html
