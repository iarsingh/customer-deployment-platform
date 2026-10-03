# Customer scenario: Meridian Labs

Meridian Labs builds internal products with eight development teams and one platform group of four. A new microservice is not a coding problem for them. It is a queue.

## What they said

> It takes our developers 2–3 days and multiple tickets to deploy a new microservice. We want developers to create a production-ready service without understanding Terraform, Kubernetes, or CI/CD.

The person in pain is a backend developer on the payments team, not the platform manager who booked the call. On a Tuesday she needed a small billing callback service. She filed four tickets: a repository, a namespace, a pipeline, and a dashboard. The namespace ticket waited on security. The pipeline ticket waited on the namespace. She was still not deployed on Thursday.

## The walk we asked for

One service, from the first ticket to the first healthy pod.

| Step | Who | System | Typical wait |
| --- | --- | --- | --- |
| Repository | Developer | GitHub ticket | Same day |
| Infrastructure | Platform | Terraform, applied from a laptop | Next day |
| Manifests | Kubernetes group | Hand-edited YAML | Next day |
| Pipeline | CI owner | Copy of another team's workflow | Same day, if the namespace exists |
| Security review | Security | Slack thread | Unbounded |
| Dashboard | Developer | Asks someone who has Grafana | Often skipped |

The decision at the end is small. The searching and the handoffs are the job.

## The constraint that deleted a design

The first design was a button labeled **Apply**. It would have run Terraform and `kubectl` from the platform API, using a cloud credential stored for the developer.

Meridian refused that. Their last production incident was a laptop `kubectl apply` against the wrong context. The platform group will not put cluster credentials in a self-service API.

What shipped instead:

- The API validates the request and renders files.
- The only writer to a cluster is Argo CD, watching a GitOps repository.
- `environment=prod` is rejected. Production is a pull request on that repository, reviewed by the platform group.
- The first template is Python. "Any language" stayed on the list and did not make the first release.

## What we will not claim

We will not claim that 2–3 days is now 10 minutes in production. That number is not measured yet.

The metric agreed before the build, with the payments developer as the judge:

- On a laptop, with no cloud login, she can submit one service request.
- Within 2 minutes she has a repository tree, a Helm render, and a policy result.
- She can point at the line that refused production and the line that refused an image tagged `latest`.
- She does not need to explain Terraform to complete the path.

A missed deployment in production is out of scope until a shadow week. This repository is the local proof, not the production claim.

## What they keep after we leave

The template, the policy files, the GitOps application, and this scenario. The platform group can add a field. They do not need the person who wrote the API to explain why production is not a dropdown.
