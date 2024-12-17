# Exercício 4 - Continuous Delivery

## Objetivos

- Compreender os princípios de Continuous Deployment.
- Demonstrar uma verificação de qualidade em Continuous Deployment, garantindo que mudanças não impactem negativamente aplicações em produção.

---

## Instruções Passo a Passo

### Introdução

Neste exercício, vamos demonstrar como um processo de verificação em Continuous Deployment pode evitar que erros impactem uma aplicação em produção. Esse processo garante um ciclo contínuo de entrega e facilita o deploy para produção de maneira simples e segura. 

Para simular essa situação, ajustaremos o critério mínimo de aceitação para rejeitar o modelo atual. Isso ilustra cenários comuns que podem ocorrer, como:

- Alterações nos dados ao re-treinar, resultando em queda de performance.
- Ajustes não intencionais no código que afetam o pipeline de treinamento.

No exercício anterior, experimentamos melhorar a acurácia do modelo. Agora, vamos simular um problema com o critério de aceitação e demonstrar como corrigi-lo.

---

### Passo 1: Ajustar o critério de aceitação

1. Abra o arquivo `cd4ml/problems/houses/ml_pipelines/default.json`.
2. Altere o valor de `acceptance_threshold_min` de `0.42` para `0.50`.
3. Faça o commit da alteração com os comandos abaixo:
   ```bash
   git add .
   git commit -m "Adjust acceptance_threshold_min from 0.42 to 0.5"
   git push