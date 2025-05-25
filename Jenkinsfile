pipeline {
    agent any

    parameters {
        choice(name: 'problem_name', choices: ['rendimento', 'insumo', 'saude_lavoura', 'commodities'], description: 'Choose the problem name')
        string(name: 'ml_pipeline_params_name', defaultValue: 'default', description: 'ML pipeline params')
        string(name: 'feature_set_name', defaultValue: 'default', description: 'Feature set')
        string(name: 'algorithm_name', defaultValue: 'default', description: 'Algorithm')
        string(name: 'algorithm_params_name', defaultValue: 'default', description: 'Algorithm params')
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    options {
        timestamps()
    }

    environment {
        DAGSTER_CONTAINER_NAME = 'dagster'
        DAGSTER_JOB = 'cd4ml_job'
        MLFLOW_TRACKING_URL = 'http://mlflow:5000'
    }

    stages {

        stage('Check code and install dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('Run Dagster job') {
            steps {
                script {
                    echo "🔥 Disparando job Dagster: ${DAGSTER_JOB}"

                    // Lança o job no container Dagster
                    sh """
                        docker exec ${DAGSTER_CONTAINER_NAME} \
                        dagster job launch \
                        --workspace /opt/dagster/app/workspace.yaml \
                        --job ${DAGSTER_JOB}
                    """
                }
            }
        }

        stage('Fetch Dagster Logs') {
            steps {
                script {
                    // (Opcional) Se tiver log persistido em arquivo
                    sh "docker logs ${DAGSTER_CONTAINER_NAME} > dagster_job.log || echo 'Log não disponível'"
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'dagster_job.log', allowEmptyArchive: true
                }
            }
        }

        stage('Check MLflow model') {
            steps {
                script {
                    def production_model_id = sh(
                        script: 'python3 scripts/check_mlflow_production.py',
                        returnStdout: true
                    ).trim()

                    if (production_model_id) {
                        echo "✅ Modelo de produção detectado: ${production_model_id}. Reiniciando o container..."
                        sh '''
                            if docker ps -a --format '{{.Names}}' | grep -q "^model$"; then
                                docker restart model
                            else
                                echo "Container 'model' não encontrado. Skipping restart."
                            fi
                        '''
                    } else {
                        echo "Nenhum novo modelo de produção encontrado. Skipping deploy."
                    }
                }
            }
        }
    }
}