# Genuine Bedrock demonstration preflight

Use the pinned Strands environment. Select a Bedrock model actually available to
the Academy AWS account in AWS_REGION and set BEDROCK_MODEL_ID. Credentials use
the AWS SDK credential chain; never put secrets in files or captures. Verify the
identity in a private terminal and confirm the chosen region/model access. Use
least-privilege bedrock:InvokeModel for the selected model/inference profile;
streaming requires bedrock:InvokeModelWithResponseStream. Cross-region inference
may require all target-region resources. Verify current model-specific IAM docs.

Offline check: construct build_strands with missing settings and confirm an
exception occurs before agent/network execution. A constructed SDK object is not
an AWS access check. Execute only one separately authorized bounded request using
`python3 -m examples.s22_agents --run --bedrock`. Retain real request/run ID,
region, model, dependency freeze, ticket fixture SHA, raw response/error and usage.
If access is denied, record that actual result; do not create a simulated success.
AWS account IDs, billing consoles and existing private resources are not teaching
materials. Source: https://docs.aws.amazon.com/bedrock/latest/userguide/security_iam_service-with-iam.html
