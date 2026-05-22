# Challenge 5: Helm Chart

## Objective

Create a Helm chart to deploy the Python HTTP server from Challenge 3 to Kubernetes.

## Background

The Challenge 3 server is a Python HTTP application that:
- Listens on **port 8080**
- Returns `200 OK` with "Everything works!" when the request includes header `Challenge: orcrist.org`
- Returns `404 Not Found` with "Wrong header!" otherwise

Assume the Docker image has been built from your Challenge 3 Dockerfile.

## Requirements

Complete the Helm chart in `server-chart/` with the following:

### 1. values.yaml
Define configurable values for:
- Container image (repository, tag, pull policy)
- Number of replicas
- Service configuration (type, port)
- Resource limits/requests (optional)

### 2. templates/deployment.yaml
Create a Kubernetes Deployment that:
- Deploys the container image
- Exposes container port 8080
- Uses values from values.yaml

### 3. templates/service.yaml
Create a Kubernetes Service that:
- Exposes the deployment
- Routes traffic to port 8080

### 4. (Optional) templates/_helpers.tpl
Add template helpers for consistent naming and labels.

## Deliverables

A working Helm chart that can be:
1. Validated with: `helm lint ./server-chart`
2. Rendered with: `helm template ./server-chart`
3. Installed with: `helm install server ./server-chart`

## Acceptance Criteria

- [x] `helm lint` passes without errors
- [x] `helm template` renders valid Kubernetes manifests
- [x] Deployment targets container port 8080
- [x] Service correctly routes to the deployment
- [x] All hardcoded values are parameterized in values.yaml

## Short explanation for files created and tasks done

**`_helpers.tpl`** defines three named templates used across both manifests:
- `server-chart.fullname` — combines release name and chart name (e.g. `server-server-chart`), truncated to 63 characters to satisfy Kubernetes label length limits
- `server-chart.labels` — full recommended label set (`app.kubernetes.io/*`) for resource identification and tooling compatibility
- `server-chart.selectorLabels` — subset of labels used in `selector.matchLabels` and pod `selector`; kept separate from the full label set because `matchLabels` is immutable after creation and should not include volatile labels like `version`

**`deployment.yaml`** uses `{{ .Values.image.repository }}:{{ .Values.image.tag }}` for the image reference rather than a pre-joined string so repository and tag can be overridden independently at install time (e.g. `--set image.tag=latest`). The container port is named `http` so the Service can reference it by name (`targetPort: http`) instead of a hardcoded number, making future port changes a single-value update in `values.yaml`.

**`service.yaml`** uses `targetPort: http` (the named port from the Deployment) rather than `targetPort: 8080` directly. This keeps the port definition canonical in one place and avoids drift if the container port value changes.

**exposure** with type `ClusterIP` choosen because an internal IP is sufficient for a test. In production better use `loadBalancer`

**resource limitation in helm chart** is set for cluster planning, admin, scaling, misbehaving pods could consume all CPU/memory on a node starving other workloads. Using reasonable defaults for a minimal Python HTTP server to handle moderate traffic. Read further https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

## Validate

Validate the chart for errors and best-practice warnings
terminal> `helm lint ./server-chart`

Render manifests locally without installing (dry-run)
terminal> `helm template ./server-chart`

Install the chart into the current Kubernetes cluster
terminal> `helm install server ./server-chart`


## How to obtain the result

### Files
Three files were created to complete the chart scaffold:

- `server-chart/templates/_helpers.tpl` — named template helpers for consistent resource naming and label sets
- `server-chart/templates/deployment.yaml` — Kubernetes Deployment manifest referencing values from `values.yaml`
- `server-chart/templates/service.yaml` — Kubernetes Service manifest routing traffic to the Deployment

`values.yaml` was already partially scaffolded; the existing values (image, replicaCount, service, resources) were kept as-is since they matched the requirements.

### Apply to minikube and test if the file validation actually works in practice

```bash
terminal> minikube start
😄  minikube v1.38.1 on Darwin 15.7.7 (arm64)
✨  Using the docker driver based on existing profile
👍  Starting "minikube" primary control-plane node in "minikube" cluster
🚜  Pulling base image v0.0.50 ...
🔄  Restarting existing docker container for "minikube" ...
🐳  Preparing Kubernetes v1.35.1 on Docker 29.2.1 ...
🔎  Verifying Kubernetes components...
    ▪ Using image gcr.io/k8s-minikube/storage-provisioner:v5
🌟  Enabled addons: default-storageclass, storage-provisioner
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
 terminal> eval $(minikube docker-env)
```

Build image, just making sure it exist and is ready
```bash
 terminal> docker build -t dhi.io/python:3.14-sfw-ent-dev ./challenge-3

[+] Building 6.5s (9/9) FINISHED                                                                                                                    ...

View build details: docker-desktop://dashboard/build/default/default/vamxfl9eau12d7jvzz5l50wp0
````

Change directory and install chart
```bash
 terminal> cd challenge-5

 terminal> helm install server ./server-chart
 terminal>

NAME: server
LAST DEPLOYED: Thu May 21 23:04:15 2026
NAMESPACE: default
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
 terminal> kubectl get pods


NAME                                  READY   STATUS    RESTARTS   AGE
server-server-chart-c4cbbf77c-2xc5k   1/1     Running   0          6s

terminal> kubectl get svc

NAME                  TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
kubernetes            ClusterIP   10.96.0.1       <none>        443/TCP    37h
server-server-chart   ClusterIP   10.105.83.196   <none>        8080/TCP   10s
```

It's running and it has an ip that we can forward locally to quickly access
```bash
kubectl port-forward svc/server-server-chart 8080:8080 

Forwarding from 127.0.0.1:8080 -> 8080
Forwarding from [::1]:8080 -> 8080
```


## In another terminal curl the result
terminal> 
```bash
curl -H "Challenge: orcrist.org" http://localhost:8080
Everything works!%
```

Looks good! Let's try with a wrong header.

terminal> 
```bash
curl http://localhost:8080`
Wrong header!%
```

Hint: The "%" seems to be a terminal new line indicator.

## Clean minikube
terminal> 
```bash
helm uninstall server
minikube stop
```