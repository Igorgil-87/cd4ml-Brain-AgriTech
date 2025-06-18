pipeline {
    agent any

    parameters {
        choice(
            name: 'problem_name',
            choices: ['rendimento', 'insumo', 'saude_lavoura', 'commodities'],
            description: 'Escolha o job Dagster a ser executado'
        )
    }

    environment {
        DAGSTER_CONTAINER_NAME = 'dagster-webserver'
        MLFLOW_TRACKING_URL = 'http://mlflow:5000'
        MLFLOW_EXPERIMENT_NAME = 'cd4ml_experiments'
    }

    options {
        timestamps()
        ansiColor('xterm')
    }

    stages {

        stage('Instalar dependências') {
            steps {
                echo "📦 Instalando dependências do projeto..."
                sh 'pip3 install --break-system-packages -r requirements.txt || echo "pip3 falhou, mas continuando..."'
            }
        }

        stage('Executar job no Dagster') {
            steps {
                script {
                    def job_name = "${params.problem_name}_job"
                    echo "🚀 Disparando o job: ${job_name}"

                    sh """
                        docker exec ${DAGSTER_CONTAINER_NAME} \
                        dagster job launch \
                        --workspace /opt/dagster/app/workspace.yaml \
                        --job ${job_name}
                    """
                }
            }
        }

        stage('Capturar logs Dagster') {
            steps {
                echo "📜 Capturando logs do container ${DAGSTER_CONTAINER_NAME}"
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
                echo "🔎 Verificando se há novo modelo em produção no MLflow"
                script {
                    def model_id = sh(
                        script: 'python3 scripts/check_mlflow_production.py',
                        returnStdout: true
                    ).trim()

                    if (model_id) {
                        echo "✅ Novo modelo encontrado com ID: ${model_id}"
                        echo "🔁 Reiniciando container model para servir novo modelo"
                        sh 'docker restart model || echo "⚠️ Container model não encontrado."'
                    } else {
                        echo "📭 Nenhum novo modelo promovido para produção."
                    }
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Pipeline concluída com sucesso!"
        }
        failure {
            echo "❌ Algo falhou. Verifique os logs e o estado do Dagster e MLflow."
        }
    }
}