terraform {
  required_version = "~>1.7.4"

  required_providers {
    helm = "~>2.12.1"
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = "~>1.14"
    }
    kubernetes = "~>2.21"
    # argocd = {
    #    source = "oboukili/argocd"
    #    version = "~>6.1.1"
    # }
  }

}

provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "minikube"
}

# Create a shared namespace to avoid replicating secrets
resource "kubernetes_namespace" "pubg_app" {
  metadata {
    labels = {
      name = "pubg-app"
    }
    name = "pubg-app"
  }
}

# provider "argocd" {
#   core = true
# }