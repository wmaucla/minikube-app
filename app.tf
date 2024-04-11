data "local_file" "pubg_secret" {
  # Normally some secret manager
  filename = "${path.module}/pubg-secret.txt"
}

resource "kubernetes_secret" "pubg_secret" {
  metadata {
    name      = "pubg-secret"
    namespace = kubernetes_namespace.pubg_app.id
  }

  data = {
    "PUBG_API_TOKEN" = data.local_file.pubg_secret.content
  }

  depends_on = [kubernetes_namespace.pubg_app]
}


# Workaround to trigger argocd
resource "null_resource" "apply_argo_cd_app" {

  // force it to run once, but after namespace created do not recreate
  triggers = {
    namespace_id = kubernetes_namespace.argocd_namespace.metadata[0].uid
  }

  provisioner "local-exec" {
    command = "kubectl apply -f argocd-app.yaml"
  }

  # Make sure we don't try and install until very end
  depends_on = [
    helm_release.bitnami_redis_cluster,
    helm_release.minio_chart,
    kubernetes_secret.repo_secret,
    null_resource.create_argocd
  ]
}