# Example infrastructure for Terragrunt

This repo show a file/folder structure
you can use with [Terragrunt](https://github.com/gruntwork-io/terragrunt) to keep your
[Terraform](https://www.terraform.io) code DRY. For background information, check out the [Keep your Terraform code
DRY](https://github.com/gruntwork-io/terragrunt#keep-your-terraform-code-dry) section of the Terragrunt documentation.

## How do you deploy the infrastructure in this repo?


### Pre-requisites

1. Install [Terraform](https://www.terraform.io/) version `0.13.0` or newer and
   [Terragrunt](https://github.com/gruntwork-io/terragrunt) version `v0.25.1` or newer.
2. Configure your AWS credentials

### Deploying a single module

1. `cd` into the module's folder (e.g. `cd aws/terraform/mentorpal/qa/us-east-1/sbert-service`).
1. Run `terragrunt plan` to see the changes you're about to apply.
1. If the plan looks good, run `terragrunt apply`.

### Deploying all modules in a region

1. `cd` into the region folder (e.g. `cd aws/terraform/mentorpal/qa/us-east-1`).
1. Run `terragrunt plan-all` to see all the changes you're about to apply.
1. If the plan looks good, run `terragrunt apply-all`.


## How is the code in this repo organized?

The code in this repo uses the following folder hierarchy:

```
account
 └ _global
 └ environment
    └ _global
    └ region
       └ resource
```

Where:

* **Account**: At the top level are each of your AWS accounts, in this case there's just one - mentorpal. 

* **Environment**: Within each account is one or more "environments", such as `qa`, `prod`, etc. 
  There may also be a `_global` folder that defines resources that are available across all the environments 
  in this AWS region, such as Route 53 A records, SNS topics, and ECR repos.

* **Region**: Within each environment, there is one or more [AWS regions](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html), 
  such as `us-east-1`, `eu-west-1`, and `ap-southeast-2`, where you've deployed resources. There may also be a `_global`
  folder that defines resources that are available across all the AWS regions in this account, such as IAM users,
  Route 53 hosted zones, and CloudTrail.

* **Resource**: Within each environment, you deploy all the resources for that environment, such as EC2 Instances, Auto
  Scaling Groups, ECS Clusters, Databases, Load Balancers, and so on. Note that the Terraform code for most of these
  resources lives in the [terragrunt-infrastructure-modules-example repo](https://github.com/gruntwork-io/terragrunt-infrastructure-modules-example).

## Creating and using root (account) level variables

In the situation where you have multiple AWS accounts or regions, you often have to pass common variables down to each
of your modules. Rather than copy/pasting the same variables into each `terragrunt.hcl` file, in every region, and in
every environment, you can inherit them from the `inputs` defined in the root `terragrunt.hcl` file.
