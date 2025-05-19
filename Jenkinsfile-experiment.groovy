pipeline {
    agent any
    parameters {
        choice(name: 'problem_name', choices: ['rendimento', 'insumo', 'saude_lavoura', 'commodities'], description: 'Choose the problem name')
        string(name: 'ml_pipeline_params_name', defaultValue: 'default', description: 'Specify the ml_pipeline_params file')
        string(name: 'feature_set_name', defaultValue: 'default', description: 'Specify the feature_set name/file')
        string(name: 'algorithm_name', defaultValue: 'default', description: 'Specify the algorithm (overrides problem_params)')
        string(name: 'algorithm_params_name', defaultValue: 'default', description: 'Specify the algorithm params')
    }
    options {
        timestamps()
    }
    environment {
        MLFLOW_TRACKING_URL = 'http://mlflow:5000'
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

        stage('Run ML Experiment') {
            steps {
                sh """
                    python3 run_python_script.py pipeline ${params.problem_name} ${params.ml_pipeline_params_name} ${params.feature_set_name} ${params.algorithm_name} ${params.algorithm_params_name} > pipeline_experiment.log 2>&1
                    cat pipeline_experiment.log
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'pipeline_experiment.log', allowEmptyArchive: true
                }
            }
        }

        stage('Acceptance + Register (Always Experimental)') {
            steps {
                sh """
                    set +e
                    python3 run_python_script.py acceptance
                    set -e
                    python3 run_python_script.py register_model ${MLFLOW_TRACKING_URL} no
                """
            }
        }
    }
}