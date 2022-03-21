data "aws_caller_identity" "current" {}

data "aws_elastic_beanstalk_hosted_zone" "current" {}

data "aws_elastic_beanstalk_solution_stack" "multi_docker" {
  most_recent = true
  name_regex  = "^64bit Amazon Linux (.*) Multi-container Docker (.*)$"
}

locals {
  namespace = "${var.eb_env_namespace}-${var.eb_env_stage}-${var.eb_env_name}"
}

module "vpc" {
  source     = "git::https://github.com/cloudposse/terraform-aws-vpc.git?ref=tags/0.25.0"
  namespace  = var.eb_env_namespace
  stage      = var.eb_env_stage
  name       = var.eb_env_name
  attributes = var.eb_env_attributes
  tags       = var.eb_env_tags
  delimiter  = var.eb_env_delimiter
  cidr_block = var.vpc_cidr_block
}

module "subnets" {
  source               = "git::https://github.com/cloudposse/terraform-aws-dynamic-subnets.git?ref=tags/0.39.3"
  availability_zones   = var.aws_availability_zones
  namespace            = var.eb_env_namespace
  stage                = var.eb_env_stage
  name                 = var.eb_env_name
  attributes           = var.eb_env_attributes
  tags                 = var.eb_env_tags
  delimiter            = var.eb_env_delimiter
  vpc_id               = module.vpc.vpc_id
  igw_id               = module.vpc.igw_id
  cidr_block           = module.vpc.vpc_cidr_block
  nat_gateway_enabled  = true
  nat_instance_enabled = false
}

module "elastic_beanstalk_application" {
  source      = "git::https://github.com/cloudposse/terraform-aws-elastic-beanstalk-application.git?ref=tags/0.11.0"
  namespace   = var.eb_env_namespace
  stage       = var.eb_env_stage
  name        = var.eb_env_name
  attributes  = var.eb_env_attributes
  tags        = var.eb_env_tags
  delimiter   = var.eb_env_delimiter
  description = var.eb_env_description
}


###
# the main elastic beanstalk env
###
module "elastic_beanstalk_environment" {
  source                     = "git::https://github.com/cloudposse/terraform-aws-elastic-beanstalk-environment.git?ref=tags/0.40.0"
  namespace                  = var.eb_env_namespace
  stage                      = var.eb_env_stage
  name                       = var.eb_env_name
  attributes                 = var.eb_env_attributes
  tags                       = var.eb_env_tags
  delimiter                  = var.eb_env_delimiter
  description                = var.eb_env_description
  region                     = var.aws_region
  availability_zone_selector = var.eb_env_availability_zone_selector
  # NOTE: We would prefer for the DNS name 
  # of module.elastic_beanstalk_environment
  # to be staticly set via inputs,
  # but have been running into other/different problems
  # trying to get that to work 
  # (for one thing, permissions error anytime try to set
  # elastic_beanstalk_environment.dns_zone_id)
  # dns_zone_id                = data.aws_elastic_beanstalk_hosted_zone.current.id
  # dns_zone_id                = var.dns_zone_id
  wait_for_ready_timeout             = var.eb_env_wait_for_ready_timeout
  elastic_beanstalk_application_name = module.elastic_beanstalk_application.elastic_beanstalk_application_name
  environment_type                   = var.eb_env_environment_type
  loadbalancer_type                  = var.eb_env_loadbalancer_type
  loadbalancer_certificate_arn       = data.aws_acm_certificate.localregion.arn
  loadbalancer_ssl_policy            = var.eb_env_loadbalancer_ssl_policy
  elb_scheme                         = var.eb_env_elb_scheme
  tier                               = "WebServer"
  version_label                      = var.eb_env_version_label
  force_destroy                      = var.eb_env_log_bucket_force_destroy

  enable_stream_logs                   = var.eb_env_enable_stream_logs
  logs_delete_on_terminate             = var.eb_env_logs_delete_on_terminate
  logs_retention_in_days               = var.eb_env_logs_retention_in_days
  health_streaming_enabled             = var.eb_env_health_streaming_enabled
  health_streaming_delete_on_terminate = var.eb_env_health_streaming_delete_on_terminate
  health_streaming_retention_in_days   = var.eb_env_health_streaming_retention_in_days

  instance_type    = var.eb_env_instance_type
  root_volume_size = var.eb_env_root_volume_size
  root_volume_type = var.eb_env_root_volume_type

  autoscale_min             = var.eb_env_autoscale_min
  autoscale_max             = var.eb_env_autoscale_max
  autoscale_measure_name    = var.eb_env_autoscale_measure_name
  autoscale_statistic       = var.eb_env_autoscale_statistic
  autoscale_unit            = var.eb_env_autoscale_unit
  autoscale_lower_bound     = var.eb_env_autoscale_lower_bound
  autoscale_lower_increment = var.eb_env_autoscale_lower_increment
  autoscale_upper_bound     = var.eb_env_autoscale_upper_bound
  autoscale_upper_increment = var.eb_env_autoscale_upper_increment

  vpc_id               = module.vpc.vpc_id
  loadbalancer_subnets = module.subnets.public_subnet_ids
  application_subnets  = module.subnets.private_subnet_ids
  allowed_security_groups = [
    module.vpc.vpc_default_security_group_id
  ]

  # NOTE: will only work for direct ssh
  # if keypair exists and application_subnets above is public subnet
  keypair = var.eb_env_keypair

  rolling_update_enabled  = var.eb_env_rolling_update_enabled
  rolling_update_type     = var.eb_env_rolling_update_type
  updating_min_in_service = var.eb_env_updating_min_in_service
  updating_max_batch      = var.eb_env_updating_max_batch

  healthcheck_url     = var.eb_env_healthcheck_url
  application_port    = var.eb_env_application_port
  solution_stack_name = data.aws_elastic_beanstalk_solution_stack.multi_docker.name
  additional_settings = var.eb_env_additional_settings
  env_vars            = var.eb_env_env_vars
  
  prefer_legacy_ssm_policy     = false
}

###
# Find a certificate for our domain that has status ISSUED
# NOTE that for now, this infra depends on managing certs INSIDE AWS/ACM
###
data "aws_acm_certificate" "localregion" {
  domain   = var.aws_acm_certificate_domain
  statuses = ["ISSUED"]
}

data "aws_acm_certificate" "cdn" {
  provider = aws.us-east-1
  domain   = var.aws_acm_certificate_domain
  statuses = ["ISSUED"]
}

data "aws_route53_zone" "main" {
  name = var.aws_route53_zone_name
}

# create dns record of type "A"
resource "aws_route53_record" "site_domain_name" {
  zone_id         = data.aws_route53_zone.main.zone_id
  name            = var.site_domain_name
  type            = "A"
  allow_overwrite = true
  alias {
    name                   = module.elastic_beanstalk_environment.endpoint
    zone_id                = data.aws_elastic_beanstalk_hosted_zone.current.id
    evaluate_target_health = true
  }
}

# find the HTTP load-balancer listener, so we can redirect to HTTPS
data "aws_lb_listener" "http_listener" {
  load_balancer_arn = module.elastic_beanstalk_environment.load_balancers[0]
  port              = 80
}

# set the HTTP -> HTTPS redirect rule for any request matching site domain
resource "aws_lb_listener_rule" "redirect_http_to_https" {
  listener_arn = data.aws_lb_listener.http_listener.arn
  action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
  condition {
    host_header {
      values = [var.site_domain_name]
    }
  }
}

######
# Cloudwatch alarms
# - https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html
######

module "notify_slack" {
  count = var.enable_alarms ? 1 : 0

  source  = "terraform-aws-modules/notify-slack/aws"
  version = "~> 4.0"

  sns_topic_name = "slack-alerts-${local.namespace}"

  lambda_function_name = "notify-slack-${local.namespace}"

  slack_webhook_url = var.cloudwatch_slack_webhook
  slack_channel     = var.slack_channel
  slack_username    = var.slack_username
}

resource "aws_cloudwatch_metric_alarm" "unhealthy_host_count" {
  count                     = var.enable_alarms ? 1 : 0
  alarm_description         = "ALB unhealthy host count (>= 1)."
  alarm_name                = "${local.namespace}-alb-unhealthy-host-count"
  namespace                 = "AWS/ApplicationELB"
  metric_name               = "UnHealthyHostCount"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  period                    = 300
  statistic                 = "Average"
  unit                      = "Count"
  threshold                 = 1
  treat_missing_data        = "notBreaching"
  actions_enabled           = true
  alarm_actions             = [one(module.notify_slack[*].this_slack_topic_arn)]
  ok_actions                = [one(module.notify_slack[*].this_slack_topic_arn)]
  insufficient_data_actions = []
  dimensions = {
    # alarm requires ARN suffix: "arn:aws:elasticloadbalancing:<region>:<account>:loadbalancer/<suffix>"
    LoadBalancer = regex(".+loadbalancer/(.*)$", module.elastic_beanstalk_environment.load_balancers[0])[0]
    # get the target group arn suffix, this is ugly, but couldn't find another way:
    TargetGroup = regex(".+:(targetgroup/.*)$", data.aws_lb_listener.http_listener.default_action[0].target_group_arn)[0]
  }
}

# LCU is defined on 4 dimensions and takes the highest one among them:
# - 25 new connections per second.
# - 3,000 active connections per minute.
# - 1 GB per hour for EC2 targets
# - 1,000 rule evaluations per second
resource "aws_cloudwatch_metric_alarm" "consumed_lcus" {
  count                     = var.enable_alarms ? 1 : 0
  alarm_description         = "ALB capacity units above the threshold (>= 1)."
  alarm_name                = "${local.namespace}-alb-consumed-lcus"
  namespace                 = "AWS/ApplicationELB"
  metric_name               = "ConsumedLCUs"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  period                    = 300
  unit                      = "Count"
  statistic                 = "Average"
  threshold                 = 1
  treat_missing_data        = "notBreaching"
  actions_enabled           = true
  alarm_actions             = [one(module.notify_slack[*].this_slack_topic_arn)]
  ok_actions                = [one(module.notify_slack[*].this_slack_topic_arn)]
  insufficient_data_actions = []
  dimensions = {
    LoadBalancer = regex(".+loadbalancer/(.*)$", module.elastic_beanstalk_environment.load_balancers[0])[0]
  }
}

resource "aws_cloudwatch_metric_alarm" "httpcode_target_5xx_count" {
  count                     = var.enable_alarms ? 1 : 0
  alarm_description         = "Beanstalk HTTP 5xx errors exceeded threshold (>= 1)."
  alarm_name                = "${local.namespace}-metric-alb-httpcode-5xx-count"
  namespace                 = "AWS/ApplicationELB"
  metric_name               = "HTTPCode_Target_5XX_Count"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  period                    = 300
  statistic                 = "Sum"
  unit                      = "Count"
  threshold                 = 1
  treat_missing_data        = "notBreaching"
  actions_enabled           = true
  alarm_actions             = [one(module.notify_slack[*].this_slack_topic_arn)]
  ok_actions                = [one(module.notify_slack[*].this_slack_topic_arn)]
  insufficient_data_actions = []
  dimensions = {
    LoadBalancer = regex(".+loadbalancer/(.*)$", module.elastic_beanstalk_environment.load_balancers[0])[0]
  }
}

resource "aws_cloudwatch_metric_alarm" "httpcode_elb_5xx_count" {
  count                     = var.enable_alarms ? 1 : 0
  alarm_description         = "Application load balancer httpcode 5xx count>(>= 1)."
  alarm_name                = "${local.namespace}-metric-alb-elb-httpcode-5xx-count"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  namespace                 = "AWS/ApplicationELB"
  metric_name               = "HTTPCode_ELB_5XX_Count"
  period                    = 300
  statistic                 = "Sum"
  unit                      = "Count"
  threshold                 = 1
  actions_enabled           = true
  treat_missing_data        = "notBreaching"
  alarm_actions             = [one(module.notify_slack[*].this_slack_topic_arn)]
  ok_actions                = [one(module.notify_slack[*].this_slack_topic_arn)]
  insufficient_data_actions = []
  dimensions = {
    LoadBalancer = regex(".+loadbalancer/(.*)$", module.elastic_beanstalk_environment.load_balancers[0])[0]
  }
}

resource "aws_cloudwatch_metric_alarm" "target_response_time" {
  count = var.enable_alarms ? 1 : 0

  alarm_name                = "${local.namespace}-alb-target-response-time"
  alarm_description         = "ALB target response time."
  metric_name               = "TargetResponseTime"
  namespace                 = "AWS/ApplicationELB"
  statistic                 = "Maximum"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = 1
  period                    = 300
  threshold                 = 10 # in seconds
  treat_missing_data        = "notBreaching"
  alarm_actions             = [one(module.notify_slack[*].this_slack_topic_arn)]
  ok_actions                = []
  insufficient_data_actions = []
  dimensions = {
    LoadBalancer = regex(".+loadbalancer/(.*)$", module.elastic_beanstalk_environment.load_balancers[0])[0]
  }
}

resource "aws_cloudwatch_metric_alarm" "response_time_p90" {
  count = var.enable_alarms ? 1 : 0

  alarm_name                = "${local.namespace}-alb-P90-target-response-time"
  alarm_description         = "P90 ALB target response time (fastest response among top 10% slowest responses)."
  metric_name               = "TargetResponseTime"
  namespace                 = "AWS/ApplicationELB"
  extended_statistic        = "p90"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = 1
  period                    = 3600
  threshold                 = 5 # in seconds
  treat_missing_data        = "notBreaching"
  alarm_actions             = [one(module.notify_slack[*].this_slack_topic_arn)]
  ok_actions                = []
  insufficient_data_actions = []
  dimensions = {
    LoadBalancer = regex(".+loadbalancer/(.*)$", module.elastic_beanstalk_environment.load_balancers[0])[0]
  }
}
