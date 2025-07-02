pipeline {
    agent any


    parameters {
        choice(
            name: 'problem_name',
            choices: ['rendimento', 'insumo', 'saude_lavoura', 'commodities'],
            description: 'Escolha o job Dagster a ser executado'
        )
    }
    //triggers {
        // Poll SCM every minute for new changes
    //    pollSCM('* * * * *')
    //}
    
    options {
       // add timestamps to output
       timestamps()
    }
    environment { 

        MLFLOW_TRACKING_URL = 'http://mlflow:5000'
        MLFLOW_S3_ENDPOINT_URL = 'http://minio:9000'
        DAGSTER_CONTAINER_NAME = 'dagster-webserver'
        MLFLOW_EXPERIMENT_NAME = 'cd4ml_experiments'
        MLFLOW_PROMOTION_THRESHOLD = '0.8'
        AWS_ACCESS_KEY_ID = "${env.ACCESS_KEY}"
        AWS_SECRET_ACCESS_KEY = "${env.SECRET_KEY}"
        PYTHONPATH = "${WORKSPACE}" 

    }
    stages {

        stage('Verificar acesso ao Docker') {
            steps {
                sh '''
                echo "\uD83D\uDC64 Usu\u00e1rio atual:"
                whoami
                echo "\uD83D\uDC65 Grupos:"
                groups
                echo "\uD83D\uDC33 Teste docker ps:"
                docker ps || echo "\u274C Sem acesso ao Docker"
                '''
            }
        }


        stage('Install dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt'
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
                script {
                    def path = "scripts/check_mlflow_production.py"
                    if (fileExists(path)) {
                        def check_result = sh(
                            script: "python3 ${path}",
                            returnStdout: true
                        ).trim()
                        if (check_result) {
                            echo "🚀 Novo modelo detectado. Reiniciando container 'model'"
                            sh 'docker restart model || echo "⚠️ Container model não encontrado."'
                        } else {
                            echo "📭 Nenhuma alteração no stage Production."
                        }
                    } else {
                        echo "⚠️ Script ${path} não encontrado."
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