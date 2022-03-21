#-------------------------------------------------------------------------------
# TERRAGRUNT CONFIGURATION
# Terragrunt is a thin wrapper for Terraform that provides extra tools for working with multiple Terraform modules,
# remote state, and locking: https://github.com/gruntwork-io/terragrunt
#-------------------------------------------------------------------------------

locals {
  # Automatically load account-level variables
  account_vars = read_terragrunt_config(find_in_parent_folders("account.hcl"))

  # Automatically load region-level variables
  region_vars = read_terragrunt_config(find_in_parent_folders("region.hcl"))

  # Automatically load environment-level variables
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))

  # Automatically load global variables
  global_vars = read_terragrunt_config(find_in_parent_folders("global.hcl"))

  # Extract the variables we need for easy access
  account_name = local.account_vars.locals.account_name
  account_id   = local.account_vars.locals.aws_account_id
  aws_region   = local.region_vars.locals.aws_region
  namespace    = local.environment_vars.locals.namespace
  environment  = local.environment_vars.locals.environment
}

# Generate an AWS provider block
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${local.aws_region}"
# without alias aws_acm_certificate throws an error: "Provider configuration not present"
# 
# │ To work with data.aws_acm_certificate.cdn its original provider
# │ configuration at provider["registry.terraform.io/hashicorp/aws"].us-east-1
# │ is required, but it has been removed. This occurs when a provider
# │ configuration is removed while objects created by that provider still exist
# │ in the state. Re-add the provider configuration to destroy
# │ data.aws_acm_certificate.cdn, after which you can remove the provider
# │ configuration again.  
  alias  = "${local.aws_region}"

  # Only these AWS Account IDs may be operated on by this template
  allowed_account_ids = ["${local.account_id}"]
}
EOF
}

remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    # name for an s3 bucket that will store terraform state
    # terragrunt will create this for us
    bucket  = "mentorpal-sberts-tf-state-${local.aws_region}"
    key     = "${path_relative_to_include()}/terraform.tfstate"
    encrypt = true
    region  = local.aws_region
    # name of the AWS dynamodb table used for locking state
    # e.g. MY_APP_NAME-s3-state-locks
    # terragrunt will create this for us
    dynamodb_table = "mentorpal-sberts-tf-locks"
  }
}

#-------------------------------------------------------------------------------
# GLOBAL PARAMETERS
# These variables apply to all configurations in this subfolder. These are automatically merged into the child
# `terragrunt.hcl` config via the include block.
#-------------------------------------------------------------------------------

# Configure root level variables that all resources can inherit. This is especially helpful with multi-account configs
# where terraform_remote_state data sources are placed directly into the modules.
inputs = merge(
  local.account_vars.locals,
  local.region_vars.locals,
  local.environment_vars.locals,
  local.global_vars.locals,
)
