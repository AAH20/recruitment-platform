# Deployment Guide — Recruitment Platform

Recruitment Platform is a Python/FastAPI service. It is containerised with the
repo `Dockerfile`, deployed with docker-compose, Kubernetes (kustomize), Helm,
or Terraform.

## Container image

```bash
docker build -t recruitment-platform:local .
docker run -p 8000:8000 -e SECRET_KEY=change-me recruitment-platform:local
# Health check
curl http://localhost:8000/health
```

The image is built `FROM python:3.12-slim`, installs `requirements.txt`, exposes
port `8000`, and its `HEALTHCHECK` calls `curl -f http://localhost:8000/health`.

## Docker Compose

```bash
# Development stack (app, db, redis, nginx, frontend, backend)
docker compose up -d

# Production compose file (lives under docker/)
docker compose -f docker/docker-compose.prod.yml up -d
```

## Kubernetes

`k8s/base` and `k8s/overlays/{development,staging,production}` are kustomize
directories. Deploy an overlay:

```bash
kubectl apply -k k8s/overlays/production/
```

Manifests include `deployment.yaml`, `service.yaml`, `ingress.yaml`,
`configmap.yaml`, and `secret.yaml`.

## Helm & Terraform

```bash
helm install recruitment-platform ./helm/
```

`terraform/` holds the infrastructure-as-code.

## Continuous Delivery (GitHub Actions)

`.github/workflows/cd.yml` builds and pushes the image (`build-and-push`), then
runs `deploy-staging` and `deploy-production`. **These deploy jobs are gated on
the repository variable `AWS_DEPLOY_ENABLED`:**

- The jobs run only when `vars.AWS_DEPLOY_ENABLED == 'true'`.
- Until it is set, the workflow builds/pushes the image, emits a `::notice::`
  that the deploy was skipped, and finishes green — **no deploy happens**.
- To enable real deploys set repository variable `AWS_DEPLOY_ENABLED=true` and
  the secrets `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`,
  `EKS_CLUSTER_NAME` (and `SLACK_WEBHOOK_URL` for notifications).

## Environment

The app runs on SQLite by default (`DATABASE_URL=sqlite:///./recruitment.db`)
and needs no external services to boot. See `.env.example` for the full list.
