# ================== STARTUP ==================

k8s:
	minikube update-check
	minikube start my-app
	minikube addons enable ingress

tf.setup:
	export KUBE_CONFIG_PATH=~/.kube/config
	terraform fmt
	terraform init

setup:
	poetry install
	poetry run mypy --install-types
	make k8s
	make publish.image
	make tf.setup

# ================== TERRAFORM ==================

tf.run:
	terraform plan
	terraform apply $(APPLY_ARGS)

# Messed up way more times than I can count
restart:
	terraform destroy
	terraform apply 

# ================== PYTHON ==================

lints:
	poetry run black pubg/* tests/
	poetry run ruff check --fix pubg/* tests/
	poetry run mypy pubg/ tests/ 

job:
	poetry run python -m pubg.jobs

api:
	poetry run gunicorn --worker-class uvicorn.workers.UvicornWorker pubg.api.main:app

# ================== PUBLISHING IMAGES ==================

# How to publish a local image to be reachable via minikube
publish.image:
	eval $(minikube docker-env) && docker build -t pubg-image .

test.run:
	docker-compose up --build test_service

production.run:
	docker-compose up --build run_core_service

# ================== TESTING ==================

# For port forwarding for testing
local.dev:
	kubectl port-forward -n pubg-app svc/bitnami-redis-cluster 6379:6379
	kubectl port-forward $(kubectl get pods --selector=app=pubg-app-deployment -o jsonpath='{.items[0].metadata.name}' -n pubg-app) 8000:8000 -n pubg-app

# prior to argocd
debug.run:
	docker build -t pubg-image .
	kubectl delete -f helm-pubg/templates/app.yaml 
	kubectl apply -f helm-pubg/templates/app.yaml


# ================== God Mode ==================

# Cluster lives and dies by this command

everything:
	make setup
	export KUBE_CONFIG_PATH=~/.kube/config
	make tf.run APPLY_ARGS="-auto-approve"