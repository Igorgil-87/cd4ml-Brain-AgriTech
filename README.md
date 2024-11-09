# CD4ML Brain AgriTech

Repositório para o projeto **CD4ML (Continuous Delivery for Machine Learning)** para a Brain AgriTech. Este ambiente Docker configura uma série de serviços e ferramentas de CI/CD para facilitar o desenvolvimento, monitoramento e implantação de modelos de machine learning. Ele integra Jenkins, Elasticsearch, Kibana, Minio, Mlflow, e Jupyter, além de scripts e dependências para suportar pipelines de machine learning e automação de testes.

## Índice

- [Visão Geral do Projeto](#visão-geral-do-projeto)
- [Serviços Configurados](#serviços-configurados)
- [Pré-requisitos](#pré-requisitos)
- [Configuração e Instalação](#configuração-e-instalação)
- [Estrutura de Contêineres e Scripts](#estrutura-de-contêineres-e-scripts)
- [Scripts de Testes e Hooks](#scripts-de-testes-e-hooks)
- [Dependências](#dependências)
- [Comandos Úteis](#comandos-úteis)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## Visão Geral do Projeto

O projeto tem como objetivo facilitar o desenvolvimento e a entrega contínua de modelos de machine learning, com um pipeline automatizado que cobre desde a preparação de dados até a implantação e monitoramento de modelos. Utiliza Docker para orquestrar os serviços necessários e configura pipelines de CI/CD através do Jenkins e ferramentas de monitoramento.

## Serviços Configurados

1. **Jenkins**: Configurado para automação de CI/CD, com plugins como BlueOcean e GitHub API. Utiliza um Dockerfile personalizado (`Dockerfile-jenkins`) para adicionar plugins, configurações de autenticação e um setup inicial.  
   - Acesse o Jenkins em: [http://localhost:10000](http://localhost:10000)

2. **Elasticsearch e Kibana**: Monitoramento e visualização de logs e dados. O Elasticsearch está configurado para uso em um cluster único, com controle de memória, e o Kibana está integrado ao Elasticsearch.
   - Acesse o Kibana em: [http://localhost:5601](http://localhost:5601)

3. **Minio**: Solução de armazenamento S3 compatível, usada para armazenar artefatos do Mlflow. Configurado para criar o bucket padrão `/data/cd4ml-ml-flow-bucket`.
   - Acesse o Minio em: [http://localhost:9000](http://localhost:9000)

4. **Mlflow**: Gerenciamento e rastreamento de experimentos de machine learning, com integração ao Minio para armazenamento de artefatos.
   - Acesse o Mlflow em: [http://localhost:12000](http://localhost:12000)

5. **Fluentd**: Configurado para coleta e monitoramento de logs dos diferentes serviços.

6. **Jupyter Notebook**: Ambiente interativo de desenvolvimento para data science e machine learning.
   - Acesse o Jupyter em: [http://localhost:8888](http://localhost:8888)

## Pré-requisitos

- **Docker** e **Docker Compose** instalados.
- Defina as variáveis de ambiente `ACCESS_KEY` e `SECRET_KEY` para autenticação no Minio e no Mlflow.

## Configuração e Instalação

1. Clone o repositório:
   ```sh
   git clone https://github.com/Igorgil-87/cd4ml-Brain-AgriTech.git
   cd cd4ml-Brain-AgriTech
2. Defina as variáveis de ambiente no terminal ou em um arquivo .env:
    export ACCESS_KEY=seu_acesso
    export SECRET_KEY=sua_chave_secreta
3. Inicie o ambiente Docker:
    docker-compose up -d

# Estrutura de Contêineres e Scripts
## Dockerfiles
    Dockerfile-jenkins: Configura o Jenkins com plugins essenciais e scripts de inicialização, permitindo automação de CI/CD personalizada.
    Dockerfile-minio: Configura o armazenamento Minio, inicializando o bucket padrão para armazenamento de artefatos de experimentos.
    Dockerfile-mlflow: Configura o servidor Mlflow para rastreamento e gerenciamento de experimentos, com armazenamento S3 através do Minio.
    Dockerfile-model: Define um serviço Flask para servir modelos de machine learning, com integração com Mlflow e configuração para logs no Fluentd.
## Scripts Auxiliares
    install_commit_hooks.sh: Configura hooks de commit, incluindo um hook de pré-commit para garantir qualidade do código, copiando-o para .git/hooks e aplicando permissões de execução.
    local_app.sh: Configura variáveis de ambiente específicas para o Flask, incluindo as integrações com Fluentd e Mlflow. Instala as dependências listadas em requirements.txt e inicia o servidor Flask na porta 5005.
    run_python_script.py: Script auxiliar para execução de funções específicas em Python dentro do ambiente Docker.

## Arquivo Jenkins
    Jenkinsfile: Define o pipeline de CI/CD para o Jenkins, automatizando etapas de build, teste e deploy para o projeto, com suporte a configurações específicas de autenticação e armazenamento de artefatos.
## Scripts de Testes e Hooks
    run_tests.sh: Script para execução de testes automatizados com pytest, gerando um relatório de cobertura de código em HTML. Também executa o flake8 para análise estática do código, ignorando avisos de print() e respeitando convenções de estilo PEP8.
## Dependências
    As dependências estão listadas no arquivo requirements.txt e incluem:
    Bibliotecas de ML e Visualização: numpy, pandas, scikit-learn, flask, mlflow, lime, bokeh
    Gerenciamento de Logs: fluent-logger
    Ferramentas de Teste e Qualidade de Código: pytest, flake8, autopep8, requests-mock

## Essas dependências são instaladas automaticamente durante o processo de build dos contêineres, mas você pode instalá-las localmente para desenvolvimento, se necessário:
    pip install -r requirements.txt

# Comandos Úteis
## Para verificar o status dos contêineres:
    docker-compose ps

## Para parar o ambiente:
    docker-compose down

## Para executar o script de testes:
    ./run_tests.sh

## Para iniciar o ambiente local do Flask:
    ./local_app.sh


## Estrutura de Pastas
    public-html/: Arquivos HTML públicos para o contêiner welcome_server.
    fluentd/conf/: Configurações para o Fluentd.
    jenkins/: Configurações e scripts específicos para Jenkins.
    cd4ml/: Diretório contendo o código-fonte principal do projeto, incluindo a aplicação Flask e outras funcionalidades de machine learning.