resource "helm_release" "minio_chart" {
  name       = "minio-pubg"
  repository = "https://charts.bitnami.com/bitnami"
  namespace  = kubernetes_namespace.pubg_app.id
  chart      = "minio"
  version    = "12.8.18"

  #   set {
  #     name  = "mode"
  #     value = "distributed"
  #   }

  depends_on = [kubernetes_namespace.pubg_app]
}
