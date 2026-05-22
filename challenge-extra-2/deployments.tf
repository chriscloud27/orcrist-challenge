resource "helm_release" "server" {
  name             = "server-chart"
  chart            = "../challenge-5/server-chart"
  namespace        = "orcrist"
  create_namespace = true

  values = [file("../challenge-5/server-chart/values.yaml")]
}
