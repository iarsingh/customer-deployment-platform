# Optional GKE target

This directory is intentionally not a Terraform root that requires Google credentials.

Meridian's first proof runs with `terraform/environments/local`. A later engagement can add a GKE cluster module here, behind a variable that defaults to off, after the laptop metric is already true.

Do not add a required `google` provider until a customer project id exists and the platform group, not a developer laptop, holds the credential. The API still must not apply that stack.
