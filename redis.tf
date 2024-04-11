data "local_file" "redis_secret" {
  # Normally some secret manager
  filename = "${path.module}/redis-admin.txt"
}


resource "helm_release" "bitnami_redis_cluster" {
  name       = "bitnami-redis-cluster"
  namespace  = kubernetes_namespace.pubg_app.id
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "redis-cluster"
  version    = "10.0.0"

  values = [templatefile("helm_config/redis/values.yaml.tpl", {
    node_count = 8 # needs minimum 6
  })]

  set {
    name  = "auth.password"
    value = data.local_file.redis_secret.content
  }

  depends_on = [kubernetes_namespace.pubg_app]
}
