#!/bin/bash

########################################
echo "📦 [INÍCIO] Setup Spinnaker com DSR"
echo "⏰ Início: $(date)"
########################################

# Diretórios base
mkdir -p spinnaker/{manifests,pipelines}

########################################
echo "📁 Criando manifests para env-a e env-b"
########################################

cat > spinnaker/manifests/env-a-deployment.yml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cd4ml-api
  namespace: env-a
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cd4ml-api
  template:
    metadata:
      labels:
        app: cd4ml-api
    spec:
      containers:
        - name: cd4ml-api
          image: cd4ml/api:latest
          ports:
            - containerPort: 8000
EOF

cat > spinnaker/manifests/env-b-deployment.yml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cd4ml-api
  namespace: env-b
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cd4ml-api
  template:
    metadata:
      labels:
        app: cd4ml-api
    spec:
      containers:
        - name: cd4ml-api
          image: cd4ml/api:latest
          ports:
            - containerPort: 8000
EOF

cat > spinnaker/manifests/service.yml <<EOF
apiVersion: v1
kind: Service
metadata:
  name: cd4ml-api
  namespace: env-a
spec:
  selector:
    app: cd4ml-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: cd4ml-api
  namespace: env-b
spec:
  selector:
    app: cd4ml-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
EOF

########################################
echo "📦 Criando pipelines DSR (YAMLs)"
########################################

cat > spinnaker/pipelines/deploy-to-a.yml <<EOF
apiVersion: v2
kind: SpinnakerPipeline
metadata:
  name: deploy-to-a
  application: cd4ml-dsr
spec:
  stages:
    - name: Deploy to env-a
      type: deployManifest
      account: my-k8s-account
      cloudProvider: kubernetes
      manifestArtifact:
        artifactAccount: embedded-artifact
        reference: spinnaker/manifests/env-a-deployment.yml
EOF

cat > spinnaker/pipelines/deploy-to-b.yml <<EOF
apiVersion: v2
kind: SpinnakerPipeline
metadata:
  name: deploy-to-b
  application: cd4ml-dsr
spec:
  stages:
    - name: Deploy to env-b
      type: deployManifest
      account: my-k8s-account
      cloudProvider: kubernetes
      manifestArtifact:
        artifactAccount: embedded-artifact
        reference: spinnaker/manifests/env-b-deployment.yml
EOF

cat > spinnaker/pipelines/rollback-a.yml <<EOF
apiVersion: v2
kind: SpinnakerPipeline
metadata:
  name: rollback-a
  application: cd4ml-dsr
spec:
  stages:
    - name: Rollback env-a
      type: undoRolloutManifest
      account: my-k8s-account
      cloudProvider: kubernetes
      options:
        namespace: env-a
        kind: deployment
        name: cd4ml-api
EOF

cat > spinnaker/pipelines/swap-traffic.yml <<EOF
apiVersion: v2
kind: SpinnakerPipeline
metadata:
  name: swap-traffic
  application: cd4ml-dsr
spec:
  stages:
    - name: Swap Traffic to env-b
      type: patchManifest
      account: my-k8s-account
      cloudProvider: kubernetes
      manifestName: service cd4ml-api
      location: env-a
      patchBody: |
        spec:
          selector:
            app: cd4ml-api
      options:
        mergeStrategy: strategic
EOF

########################################
echo "📦 Criando namespaces env-a e env-b"
########################################

for ns in env-a env-b; do
  if ! kubectl get ns "$ns" &>/dev/null; then
    echo "📁 Criando namespace: $ns"
    kubectl create namespace "$ns"
  else
    echo "✅ Namespace já existe: $ns"
  fi
done

########################################
echo "🚀 Aplicando manifests"
########################################

kubectl apply -f spinnaker/manifests/env-a-deployment.yml
kubectl apply -f spinnaker/manifests/env-b-deployment.yml
kubectl apply -f spinnaker/manifests/service.yml