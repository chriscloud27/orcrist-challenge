# Challenge Extra 2

Provision the `server-chart` Helm chart (from `challenge-5`) into a local Kubernetes cluster using Terraform.

---

## Prerequisites
I am working on a macOS.

| Tool | Install |
|---|---|
| [minikube](https://minikube.sigs.k8s.io/docs/start/) | `brew install minikube` |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | `brew install kubectl` |
| [Helm](https://helm.sh/docs/intro/install/) | `brew install helm` |
| [Terraform](https://developer.hashicorp.com/terraform/install) | `brew tap hashicorp/tap && brew install hashicorp/tap/terraform` |


## Files

### `providers.tf`
Declares the required Terraform providers and configures them to use the local kubeconfig.

### `deployments.tf`
Deploys the `server-chart` Helm chart into the `orcrist` namespace. The namespace is created automatically if it does not exist.

## Commands
**Start and apply**
```bash
minikube start
terraform init
terraform plan
terraform apply
```

"yes"

**Verify the Helm release and running pods**
```bash
helm list -n orcrist
kubectl get all -n orcrist
```

All running as expected. Minimal setup.


## Short explanation

Terraform uses the `hashicorp/helm` provider to deploy a local Helm chart (`challenge-5/server-chart`) into minikube. The `create_namespace = true` flag removes the need for a separate namespace resource — Helm creates `orcrist` automatically on first apply. Values are sourced directly from the chart's existing `values.yaml`.
