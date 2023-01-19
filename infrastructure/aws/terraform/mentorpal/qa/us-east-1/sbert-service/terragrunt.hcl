locals {
  # Automatically load environment-level variables
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  region_vars      = read_terragrunt_config(find_in_parent_folders("region.hcl"))
  account_vars     = read_terragrunt_config(find_in_parent_folders("account.hcl"))
  secret_vars      = read_terragrunt_config("./secret.hcl")
  # Extract out common variables for reuse
  env                      = local.environment_vars.locals.environment
  aws_account_id           = local.account_vars.locals.aws_account_id
  aws_region               = local.region_vars.locals.aws_region
  cloudwatch_slack_webhook = local.secret_vars.locals.cloudwatch_slack_webhook
  sentry_dsn_sbert         = local.secret_vars.locals.sentry_dsn_sbert
  api_secret_key           = local.secret_vars.locals.api_secret_key
  jwt_secret_key           = local.secret_vars.locals.jwt_secret_key
  secret_header_name       = local.secret_vars.locals.secret_header_name
  secret_header_value      = local.secret_vars.locals.secret_header_value
  allowed_origin           = local.secret_vars.locals.allowed_origin
}

terraform {
  source = "${path_relative_from_include()}//modules/beanstalk"
}

# Include all settings from the root terragrunt.hcl file
# include "root" { # VS code doesnt highlight this correctly
include {
  path = find_in_parent_folders()
}

inputs = {
  aws_region                 = local.aws_region
  aws_availability_zones     = ["us-east-1a", "us-east-1b"]
  vpc_cidr_block             = "10.10.0.0/16"
  aws_acm_certificate_domain = "mentorpal.org"
  aws_route53_zone_name      = "mentorpal.org"
  site_domain_name           = "sbert-qa.mentorpal.org"
  eb_env_namespace           = "mentorpal"
  eb_env_stage               = local.env
  eb_env_name                = "sbert"
  eb_env_instance_type       = "c6i.large" # compute-optimized, 60$/month, similar to t3.large
  enable_alarms              = true
  slack_channel              = "ls-alerts-qa"
  slack_username             = "uscictlsalerts"
  cloudwatch_slack_webhook   = local.cloudwatch_slack_webhook
    secret_header_name       = local.secret_header_name
  secret_header_value        = local.secret_header_value
  allowed_origin             = local.allowed_origin

  # scaling:
  eb_env_autoscale_min = 1 # ~23req/sec with c6i.large
  eb_env_autoscale_max = 1 # ~50req/sec with c6i.large
  # seems like there's no way to set desired capacity and it seems to be max by default?
  eb_env_autoscale_measure_name    = "CPUUtilization"
  eb_env_autoscale_statistic       = "Average"
  eb_env_autoscale_unit            = "Percent"
  eb_env_autoscale_lower_bound     = "20"
  eb_env_autoscale_lower_increment = "1"
  eb_env_autoscale_upper_bound     = "80"
  eb_env_autoscale_upper_increment = "1"

  eb_env_env_vars = {
    STAGE                           = local.env,
    IS_SENTRY_ENABLED               = "true",
    SENTRY_DSN_MENTOR_SBERT_SERVICE = local.sentry_dsn_sbert,
    LOG_LEVEL_SBERT_SERVICE         = "DEBUG",
    API_SECRET_KEY                  = local.api_secret_key,
    JWT_SECRET_KEY                  = local.jwt_secret_key,

  }

  # logging:
  eb_env_enable_stream_logs                   = true
  eb_env_logs_delete_on_terminate             = false
  eb_env_logs_retention_in_days               = 30
  eb_env_health_streaming_enabled             = true
  eb_env_health_streaming_delete_on_terminate = false
  eb_env_health_streaming_retention_in_days   = 7
  eb_env_tags = {
    Terraform   = "true"
    Environment = local.env
    Project     = "mentorpal"
    Service     = "sbert"
  }
}
