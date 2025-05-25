pipeline {
    agent any

    parameters {
        choice(name: 'problem_name', choices: ['rendimento', 'insumo', 'saude_lavoura', 'commodities'], description: 'Escolha o problema a ser executado')
    }

    environment {
        DAGSTER_CONTAINER_NAME = 'dagster'
        MLFLOW_TRACKING_URL = 'http://mlflow:5000'
    }

    options {
        timestamps()
    }

    stages {
        stage('Instalar dependências') {
            steps {
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('Executar job Dagster') {
            steps {
                echo "🎯 Executando Dagster job: ${params.problem_name}_job"
                sh """
                    docker exec ${DAGSTER_CONTAINER_NAME} \
                    dagster job launch \
                    --workspace /opt/dagster/app/workspace.yaml \
                    --job ${params.problem_name}_job
                """
            }
        }

        stage('Capturar logs') {
            steps {
                sh "docker logs ${DAGSTER_CONTAINER_NAME} > dagster_job.log || echo 'Log indisponível'"
            }
            post {
                always {
                    archiveArtifacts artifacts: 'dagster_job.log', allowEmptyArchive: true
                }
            }
        }

        stage('Verificar modelo no MLflow') {
            steps {
                script {
                    def model_id = sh(
                        script: 'python3 scripts/check_mlflow_production.py',
                        returnStdout: true
                    ).trim()
                    if (model_id) {
                        echo "🔁 Reiniciando container model..."
                        sh 'docker restart model || echo "model container não encontrado."'
                    } else {
                        echo "📭 Nenhum novo modelo em produção."
                    }
                }
            }
        }
    }
}