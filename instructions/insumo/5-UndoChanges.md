# Continuous Deployment - Reverter Alterações

## Objetivos

- Observar a etapa de aceitação do pipeline de Continuous Deployment.
- Aprender como reverter seu código para um commit anterior.

---

## Passos

1. Abra o arquivo `cd4ml/ml_model_params.py`.

2. Ajuste o número de `n_estimators` no modelo de `random_forests` de **50** para **5**.

3. Faça o commit e envie suas alterações para o repositório:
   ```bash
   git add cd4ml/ml_model_params.py
   git commit -m "Adjust number of n_estimators to 5"
   git push