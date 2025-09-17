# Setup do Spinnaker em Kubernetes (Docker Desktop) com MySQL para Front50

## Visão Geral
Este documento descreve o passo a passo completo para subir o **Spinnaker distribuído** em um cluster Kubernetes local (Docker Desktop), usando **MySQL como backend do Front50**.

- **Maior desafio:** `front50` em `CrashLoopBackOff` devido ao arquivo `front50-local.yml` gerado pelo Halyard com `spring.profiles.include` (incompatível com Spring Boot 2.4+).
- **Solução:** sobrepor o arquivo “ruim” com um `ConfigMap` correto, ativar o profile `sql` via variável de ambiente e garantir apenas **um diretório de config válido** para o Spring Boot.

---

## 1. Criar namespace e banco de dados MySQL

```bash
kubectl create ns spinnaker

kubectl -n spinnaker run mysql \
  --image=mariadb:10.6 \
  --env="MYSQL_ROOT_PASSWORD=123" \
  --env="MYSQL_DATABASE=front50" \
  --port=3306

kubectl -n spinnaker expose pod mysql --port=3306



Teste de conectividade:
kubectl -n spinnaker run sql-client --rm -it --restart=Never \
  --image=mariadb:10.6 -- \
  mysql -hmysql -uroot -p123 -e "SELECT 1;"

  2. Subir o Halyard em container
  docker run -it --name halyard --rm \
  -v ~/.hal:/home/spinnaker/.hal \
  -v ~/.kube:/home/spinnaker/.kube \
  us-docker.pkg.dev/spinnaker-community/docker/halyard:stable bash


  Ajustar kubeconfig dentro do container
  kubectl config set-cluster docker-desktop \
  --server=https://kubernetes.docker.internal:6443 \
  --insecure-skip-tls-verify=true

  ⚠️ Importante:
Do host usamos 127.0.0.1:6443, mas dentro do container é necessário kubernetes.docker.internal:6443.

3. Configuração básica via hal
hal config version edit --version 1.30.1
hal config provider kubernetes enable
hal config provider kubernetes account add another-account --context docker-desktop
hal config deploy edit --type distributed --account-name another-account
hal config storage edit --type redis
hal config deploy edit --location spinnaker

4. Criar ConfigMap limpo para o Front50
kubectl -n spinnaker apply -f - <<'YAML'
apiVersion: v1
kind: ConfigMap
metadata:
  name: front50-local
data:
  front50-local.yml: |
    sql:
      enabled: true
      connectionPools:
        default:
          default: true
          jdbcUrl: jdbc:mysql://mysql:3306/front50?useSSL=false
          user: root
          password: 123
          driverClassName: org.mariadb.jdbc.Driver
      migration:
        jdbcUrl: jdbc:mysql://mysql:3306/front50?useSSL=false
        user: root
        password: 123
    spinnaker:
      redis:
        enabled: false
YAML

5. Corrigir montagens do front50
	1.	Remover mounts duplicados (vindos do Secret do Halyard):

    IDX=$(kubectl -n spinnaker get deploy spin-front50 -o json \
    | jq -r '.spec.template.spec.containers[0].volumeMounts
        | to_entries[] 
        | select(.value.mountPath=="/opt/spinnaker/config/front50-local.yml") 
        | .key' | tail -1)

    kubectl -n spinnaker patch deploy spin-front50 --type=json -p="[
    {\"op\":\"remove\",\"path\":\"/spec/template/spec/containers/0/volumeMounts/$IDX\"}
    ]"

    2.	Montar apenas os arquivos necessários:
    kubectl -n spinnaker patch deploy spin-front50 --type='json' -p='[
    {"op":"add","path":"/spec/template/spec/volumes/-",
    "value":{"name":"config-merged","emptyDir":{}}}
    ]'

    kubectl -n spinnaker patch deploy spin-front50 --type='json' -p='[
    {"op":"add","path":"/spec/template/spec/containers/0/volumeMounts/-",
    "value":{"name":"config-merged","mountPath":"/opt/spinnaker/config"}}
    ]'

    kubectl -n spinnaker patch deploy spin-front50 --type='json' -p='[
    {"op":"add","path":"/spec/template/spec/containers/0/volumeMounts/-",
    "value":{"name":"front50-local","mountPath":"/opt/spinnaker/config/front50-local.yml","subPath":"front50-local.yml"}}
    ]'

6. Variáveis de ambiente corretas
kubectl -n spinnaker set env deploy/spin-front50 --overwrite \
  SPRING_PROFILES_ACTIVE='local,sql' \
  SPRING_CONFIG_LOCATION='file:/opt/spinnaker/config/' \
  JAVA_OPTS='-XX:MaxRAMPercentage=50.0 -Dlogging.file.name=/dev/stdout'

7. Aplicar e reiniciar
hal deploy apply
kubectl -n spinnaker rollout restart deploy/spin-front50
kubectl -n spinnaker rollout status deploy/spin-front50


Logs de sucesso do Front50:
	•	Tomcat started on port(s): 8080
	•	Started Main in … seconds
	•	{"status":"UP"} em /health


kubectl -n spinnaker run netcheck --rm -it --restart=Never --image=busybox:1.36 -- \
  sh -lc 'wget -qO- http://spin-front50:8080/health || true'


8. Acesso à UI e API
kubectl -n spinnaker port-forward svc/spin-deck 9000:9000
kubectl -n spinnaker port-forward svc/spin-gate 8084:8084

Dificuldades e Surpresas
	•	Halyard x kubeconfig: caminho do API server muda dentro do container (127.0.0.1 vs kubernetes.docker.internal).
	•	Front50 Storage: não basta hal config storage; precisa habilitar sql via env.
	•	Spring Boot 2.4+: spring.profiles.include em arquivos montados gera InvalidConfigDataPropertyException.
	•	Secret do Halyard: injetava um front50-local.yml ruim → tivemos que sobrescrever com ConfigMap.
	•	Rollout travando: pods antigos demorando a encerrar → usar --previous para logs.
	•	VolumeMounts duplicados: erro must be unique corrigido removendo mounts redundantes.

Conclusão

Agora o Spinnaker sobe estável com front50 apontando para MySQL.
Este fluxo documenta as correções e armadilhas que encontramos — principalmente a forma como o Spring Boot 2.4 lida com perfis e como o Halyard injeta configs por Secret.
