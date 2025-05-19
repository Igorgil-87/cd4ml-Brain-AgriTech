pipeline {
    agent any
    parameters {
        choice(name: 'problem_name', choices: ['rendimento', 'insumo', 'saude_lavoura', 'commodities'], description: 'Choose the problem name')
        string(name: 'ml_pipeline_params_name', defaultValue: 'default', description: 'Specify the ml_pipeline_params file')
        string(name: 'feature_set_name', defaultValue: 'default', description: 'Specify the feature_set name/file')
        string(name: 'algorithm_name', defaultValue: 'default', description: 'Specify the algorithm (overrides problem_params)')
        string(name: 'algorithm_params_name', defaultValue: 'default', description: 'Specify the algorithm params')
    }
    triggers {
        pollSCM('H/5 * * * *') // Check every 5 minutes
    }
    options {
        timestamps()
    }
    environment {
        MLFLOW_TRACKING_URL = 'http://mlflow:5000'
        MLFLOW_S3_ENDPOINT_URL = 'http://minio:9000'
        AWS_ACCESS_KEY_ID = "${env.ACCESS_KEY}"
        AWS_SECRET_ACCESS_KEY = "${env.SECRET_KEY}"
        PYTHONPATH = "${WORKSPACE}"
    }
    stages {

        stage('Install dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('Fetch Data') {
            steps {
                sh 'python3 cd4ml/problems/commodities/download_data/download_data.py'
            }
        }

        stage('Run tests') {
            steps {
                script {
                    def TEST_DIR = "cd4ml/problems/${params.problem_name}/tests"
                    sh """
                        set -e
                        echo "=== Rodando testes em: ${TEST_DIR} ==="
                        pytest ${TEST_DIR} --maxfail=2 --disable-warnings --tb=short | tee test_execution.log
                    """
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'test_execution.log', allowEmptyArchive: true
                }
            }
        }

        stage('Run ML pipeline') {
            steps {
                sh """
                    python3 run_python_script.py pipeline ${params.problem_name} ${params.ml_pipeline_params_name} ${params.feature_set_name} ${params.algorithm_name} ${params.algorithm_params_name} > pipeline.log 2>&1
                    cat pipeline.log
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'pipeline.log', allowEmptyArchive: true
                }
            }
        }

        stage('Production - Register Model and Acceptance Test') {
            when {
                allOf {
                    equals expected: 'default', actual: "${params.ml_pipeline_params_name}"
                    equals expected: 'default', actual: "${params.feature_set_name}"
                    equals expected: 'default', actual: "${params.algorithm_name}"
                    equals expected: 'default', actual: "${params.algorithm_params_name}"
                }
            }
            steps {
                sh 'python3 run_python_script.py acceptance'
            }
            post {
                success {
                    sh 'python3 run_python_script.py register_model ${MLFLOW_TRACKING_URL} yes'
                }
                failure {
                    sh 'python3 run_python_script.py register_model ${MLFLOW_TRACKING_URL} no'
                }
            }
        }

        stage('Experiment - Register Model and Acceptance Test') {
            when {
                anyOf {
                    not { equals expected: 'default', actual: "${params.ml_pipeline_params_name}" }
                    not { equals expected: 'default', actual: "${params.feature_set_name}" }
                    not { equals expected: 'default', actual: "${params.algorithm_name}" }
                    not { equals expected: 'default', actual: "${params.algorithm_params_name}" }
                }
            }
            steps {
                sh """
                    set +e
                    python3 run_python_script.py acceptance
                    set -e
                    python3 run_python_script.py register_model ${MLFLOW_TRACKING_URL} no
                """
            }
        }

        stage('Deploy Model') {
            steps {
                script {
                    def production_model_id = sh(script: 'python3 scripts/check_mlflow_production.py', returnStdout: true).trim()
                    if (production_model_id) {
                        echo "New production model found: ${production_model_id}. Restarting 'model' container..."
                        sh '''
                            if docker ps -a --format '{{.Names}}' | grep -q "^model$"; then
                                docker restart model
                            else
                                echo "Container 'model' not found. Skipping restart."
                            fi
                        '''
                    } else {
                        echo "No new production model found. Skipping deploy."
                    }
                }
            }
        }
    }
}