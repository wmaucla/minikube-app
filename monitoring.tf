resource "kubernetes_namespace" "monitoring_namespace" {
  metadata {
    name = "monitoring"
  }
}


resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "prometheus"
  namespace  = kubernetes_namespace.monitoring_namespace.id
  version    = "25.19.0"

  depends_on = [kubernetes_namespace.monitoring_namespace]
}

resource "helm_release" "grafana" {
  name       = "grafana"
  repository = "https://grafana.github.io/helm-charts"
  namespace  = kubernetes_namespace.monitoring_namespace.id
  chart      = "grafana"
  version    = "7.3.7"

  set {
    name  = "adminPassword" # Change this to set your Grafana admin password
    value = "your_password"
  }

  depends_on = [kubernetes_namespace.monitoring_namespace]
}

