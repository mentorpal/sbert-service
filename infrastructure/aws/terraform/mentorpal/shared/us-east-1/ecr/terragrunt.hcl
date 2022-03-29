locals {
  account_vars   = read_terragrunt_config(find_in_parent_folders("account.hcl"))
  aws_account_id = local.account_vars.locals.aws_account_id
}

terraform {
  source = "${path_relative_from_include()}//modules/ecr"
}

# Include all settings from the root terragrunt.hcl file
include {
  path = find_in_parent_folders()
}

inputs = {
  repository_name      = "sbert_service"
  image_tag_mutability = "MUTABLE"
  scan_on_push         = true
  access_principals = [
    "arn:aws:iam::${local.aws_account_id}:root",
    # for multi-account setup:
    # "arn:aws:iam::${local.dev_account_id}:root",
    # "arn:aws:iam::${local.staging_account_id}:root",
    # "arn:aws:iam::${local.production_account_id}:root"
  ]
}
