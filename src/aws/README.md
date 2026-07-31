# AWS

This folder will contain AWS-specific configuration, scripts, and integration code for deploying and connecting the framework's cloud services.

## Planned Contents
- `lambda/` — AWS Lambda function code that receives prediction output and triggers scheduling actions on the Kubernetes cluster
- `iam/` — IAM role and policy definitions for secure access between services (EKS, Lambda, S3, SageMaker)
- `cloudwatch/` — CloudWatch configuration for monitoring container/cluster resource metrics
- `s3/` — S3 bucket configuration and helper scripts for storing raw and processed workload data
- `eks/` — EKS cluster configuration files (deployment manifests, autoscaling config)

## Purpose
Connects the AI prediction model (in `ai_models/`) to the AWS infrastructure layer, enabling the framework's predicted resource demand to actually influence container scheduling on AWS.

## Status
Not yet implemented — Phase-I is planning and architecture only. Service selection is finalized in the AWS Services Planning table in `documentation/`.