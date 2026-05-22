## Namespaces
terminal> `kubectl get ns``

## All pods from all ns
terminal> `kubectl get pods --all-namespaces`

## All services from namespace orcrist
terminal> `kubectl get svc -n orcrist`

## Image from nginx deployment on orcrist ns
Get all data with the IMAGES
terminal> `kubectl get deploy -n orcrist -o wide`
Showing IMAGES "nginx:latest"

## Create port-forward
terminal> `k port-forward deployment/nginx-deployment -n orcrist 8080:80`
terminal> `curl http://localhost:8080`

