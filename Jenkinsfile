pipeline {
    agent any

    triggers {
        // Executa pipeline a cada push na branch main (via webhook ou polling)
        githubPush()
    }

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
        MLFLOW_PROMOTION_THRESHOLD = '0.8'
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

        stage('Verificar R2 e promover modelo') {
            steps {
                echo "🧠 Avaliando performance do modelo e promovendo se adequado..."
                script {
                    def scriptPath = "scripts/promote_model_if_good.py"
                    def result = sh(
                        script: "python3 ${scriptPath} --model ${params.problem_name} --threshold ${MLFLOW_PROMOTION_THRESHOLD}",
                        returnStatus: true
                    )
                    if (result == 0) {
                        echo "✅ Modelo promovido com sucesso para Production."
                    } else {
                        echo "🔒 Modelo não atingiu o threshold de R2."
                    }
                }
            }
        }

        stage('Reiniciar API se houver modelo novo') {
            steps {
                echo "🔁 Verificando e reiniciando container de API se houver modelo novo"
                script {
                    def check_result = sh(
                        script: 'python3 scripts/check_mlflow_production.py',
                        returnStdout: true
                    ).trim()

                    if (check_result) {
                        echo "🚀 Novo modelo detectado. Reiniciando container 'model'"
                        sh 'docker restart model || echo "⚠️ Container model não encontrado."'
                    } else {
                        echo "📭 Nenhuma alteração no stage Production."
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
