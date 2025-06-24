pipeline {
    agent any


    parameters {
        choice(
            name: 'problem_name',
            choices: ['rendimento', 'insumo', 'saude_lavoura', 'commodities'],
            description: 'Escolha o job Dagster a ser executado'
        )
    }
    triggers {
        // Poll SCM every minute for new changes
        pollSCM('* * * * *')
    }
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



    }
}