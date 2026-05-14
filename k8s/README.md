# Kubernetes & Helm Support

This directory contains Kubernetes manifests and Helm charts for deploying the Talent Acquisition Agent to a Kubernetes cluster.

## Directory Structure

```
k8s/
├── base/           # Base Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── api-deployment.yaml
│   ├── search-deployment.yaml
│   ├── web-deployment.yaml
│   ├── mongodb-deployment.yaml
│   ├── ingress.yaml
│   └── network-policy.yaml
└── overlays/        # Kustomize overlays for different environments
    ├── dev/
    │   └── kustomization.yaml
    └── prod/
        └── kustomization.yaml

helm/
└── job-agent/      # Helm chart
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── _helpers.tpl
        ├── 00-namespace.yaml
        ├── 01-configmap.yaml
        ├── 02-api.yaml
        ├── 03-search.yaml
        ├── 04-web.yaml
        ├── 05-mongodb.yaml
        ├── 06-ingress.yaml
        └── 07-serviceaccount.yaml
```

## Quick Start

### Option 1: Using Helm (Recommended)

```bash
# Add the chart repository
helm repo add job-agent https://your-org.github.io/helm-charts

# Install the chart
helm install job-agent job-agent/job-agent \
  --namespace job-agent \
  --create-namespace \
  --set image.repository=ghcr.io/your-org/job-agent

# Upgrade the chart
helm upgrade job-agent job-agent/job-agent \
  --namespace job-agent \
  --set image.tag=v1.0.0

# Uninstall
helm uninstall job-agent --namespace job-agent
```

### Option 2: Using Kustomize

```bash
# Apply dev environment
kubectl apply -k k8s/overlays/dev

# Apply prod environment
kubectl apply -k k8s/overlays/prod
```

### Option 3: Using raw YAML

```bash
# Apply base manifests
kubectl apply -f k8s/base/
```

## Configuration

### Helm Values

Key configuration options in `values.yaml`:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas per service | 2 |
| `image.repository` | Container registry | `ghcr.io/your-org/job-agent` |
| `image.tag` | Image tag | `1.0` |
| `service.type` | Service type (ClusterIP/LoadBalancer) | ClusterIP |
| `ingress.enabled` | Enable Ingress | true |
| `ingress.className` | Ingress class | nginx |
| `mongodb.enabled` | Enable MongoDB | true |
| `autoscaling.enabled` | Enable HPA | false |

### Environment-Specific Configuration

**Development:**
```bash
helm install job-agent job-agent/job-agent \
  --namespace job-agent-dev \
  --create-namespace \
  -f helm/job-agent/values.yaml \
  --set replicaCount=1
```

**Production:**
```bash
helm install job-agent job-agent/job-agent \
  --namespace job-agent-prod \
  --create-namespace \
  -f helm/job-agent/values.yaml \
  --set replicaCount=3 \
  --set autoscaling.enabled=true
```

## Image Building

Build and push container images:

```bash
# Build API image
docker build -t ghcr.io/your-org/job-agent/api:latest -f services/api/Dockerfile .

# Build Search image
docker build -t ghcr.io/your-org/job-agent/search:latest -f services/search/Dockerfile .

# Build Web image
docker build -t ghcr.io/your-org/job-agent/web:latest -f services/web/Dockerfile .

# Push to registry
docker push ghcr.io/your-org/job-agent/api:latest
docker push ghcr.io/your-org/job-agent/search:latest
docker push ghcr.io/your-org/job-agent/web:latest
```

## Health Checks

All services include:
- **Liveness Probe**: `/health` - confirms the container is running
- **Readiness Probe**: `/ready` - confirms the service can accept traffic

Update the health check paths in your service code if different:

```python
# In services/api/app.py
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}
```

## Network Policies

The base manifests include a `NetworkPolicy` that restricts:
- **Ingress**: Only from ingress-nginx namespace or within the job-agent namespace
- **Egress**: DNS (port 53) and intra-pod communication

Adjust network policies based on your cluster's CNI and requirements.

## Ingress Configuration

The ingress routes:
- `/api/*` → API service (port 8080)
- `/search/*` → Search service (port 8081)
- `/*` → Web service (port 3000)

Update the host in `values.yaml` or the ingress manifest for your domain:

```yaml
ingress:
  hosts:
    - host: jobs.yourdomain.com
```

## Monitoring

For Prometheus monitoring, enable in values:

```yaml
prometheus:
  enabled: true
  scrape: true
  port: 9090
```

Add annotations to your deployments:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"
  prometheus.io/path: "/metrics"
```

## Security Considerations

1. **Secrets**: Add secrets via `--set` or external secrets operator
2. **Network Policies**: Review and adjust for your environment
3. **RBAC**: ServiceAccount is created automatically
4. **TLS**: Enable TLS in ingress configuration for production
