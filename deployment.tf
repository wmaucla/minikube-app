resource "kubernetes_namespace" "argocd_namespace" {
  metadata {
    name = "argocd"
  }
}


resource "null_resource" "create_argocd" {

  // force it to run once, but after namespace created do not recreate
  triggers = {
    namespace_id = kubernetes_namespace.argocd_namespace.metadata[0].uid
  }

  provisioner "local-exec" {
    command = "kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"
  }

  depends_on = [
    kubernetes_namespace.argocd_namespace
  ]
}


data "local_file" "github_ssh_private_key" {
  # Normally some secret manager
  filename = "${path.module}/ssh-private-key.txt"
}


resource "kubernetes_secret" "repo_secret" {
  metadata {
    name      = "repo-422312180"
    namespace = "argocd"

    labels = {
      "argocd.argoproj.io/secret-type" = "repository"
    }
  }

  data = {
    name          = "minikube-app"
    project       = "default"
    sshPrivateKey = data.local_file.github_ssh_private_key.content
    type          = "git"
    url           = "git@github.com:wmaucla/minikube-app.git"
  }

  depends_on = [
    kubernetes_namespace.argocd_namespace,
    data.local_file.github_ssh_private_key,
  ]
}

// kubectl delete -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml