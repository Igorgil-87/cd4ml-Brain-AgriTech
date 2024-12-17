# Continuous Deployment - Configuração

## Objetivos

- Aprender os princípios de Continuous Deployment.
- Compreender as etapas de um `Jenkinsfile`.
- Aprender como adicionar uma nova etapa no Jenkins.

---

## Visão Geral

Neste ponto, já criamos um modelo com ótimo desempenho preditivo. Agora, queremos garantir que o desempenho do modelo não apresente regressões. Para isso, adicionaremos uma etapa ao `Jenkinsfile` para verificar o desempenho do modelo.

---

## Passos

1. Abra o arquivo `Jenkinsfile`.

2. Descomente o bloco **"Acceptance Test"**:
   - Remova as barras duplas (`//`) no início das linhas referentes ao bloco de teste.

3. Faça o commit e envie suas alterações para o repositório:
   ```bash
   git add .
   git commit -m "Adding Jenkins Continuous Deployment check"
   git push