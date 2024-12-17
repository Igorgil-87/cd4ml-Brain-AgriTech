# Exercício 6: Monitoramento e Observabilidade do Modelo

## Objetivos

- Conhecer o stack EFK ([Elasticsearch](https://www.elastic.co/products/elasticsearch), 
  [FluentD](https://www.fluentd.org/) e [Kibana](https://www.elastic.co/products/kibana)).
- Configurar e implantar a aplicação para registrar eventos de predição no Elasticsearch.
- Visualizar os eventos no dashboard do Kibana.
- Aprender como fechar o ciclo de feedback de dados.

---

## Introdução

Para fechar o ciclo de feedback de dados, podemos registrar eventos em produção para coletar informações sobre como nosso modelo está se comportando com dados reais. Esses dados podem ser posteriormente curados e rotulados para melhorar o conjunto de dados usado durante o treinamento. Isso nos permite aprimorar continuamente os modelos em produção!

Neste workshop, utilizamos o stack EFK para monitoramento e infraestrutura de observabilidade, composto pelos seguintes componentes principais:

- [Elasticsearch](https://www.elastic.co/products/elasticsearch): um mecanismo de busca de código aberto.
- [FluentD](https://www.fluentd.org/): um coletor de dados de código aberto para unificação de logs.
- [Kibana](https://www.elastic.co/products/kibana): uma interface web de código aberto que facilita a exploração e visualização dos dados indexados pelo Elasticsearch.

---

## Instruções Passo a Passo

1. Certifique-se de que você executou recentemente o Pipeline no Jenkins para carregar um modelo.
2. Navegue até o [Serviço do Modelo](http://localhost:11000).
3. Selecione um horário e um produto, e clique em **Submit**.
4. Acesse o [Kibana](http://localhost:5601).

   ![Página Inicial do Kibana](./images/KibanaHomePage.png)

5. Na página inicial, clique na bússola "Discover" no canto superior esquerdo. Isso o levará para a página "Create Index Pattern". Insira `model-*` como o padrão de índice. Clique em **Next Step**.

   ![Criar Padrão de Índice no Kibana](./images/KibanaCreateIndex.png)

6. Na página "Configure Settings", certifique-se de que `@timestamp` esteja selecionado no menu suspenso "Time Filter Field name". Clique em **Create Index Pattern**.

   ![Filtro de Tempo no Kibana](./images/KibanaTimeFilter.png)

7. Clique novamente na bússola "Discover" no canto superior esquerdo. Agora você deve conseguir visualizar os logs do modelo, incluindo horários, nomes de produtos e predições realizadas.

   ![Predições do Modelo no Kibana](./images/KibanaPredictions.png)

---

## Finalizando o Ambiente

Para parar o ambiente, execute:
```bash
docker-compose down