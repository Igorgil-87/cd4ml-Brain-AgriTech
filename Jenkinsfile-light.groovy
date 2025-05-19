pipeline {
    agent any
    parameters {
        choice(name: 'problem_name', choices: ['rendimento', 'insumo', 'saude_lavoura', 'commodities'], description: 'Choose the problem name')
    }
    options {
        timestamps()
    }
    environment {
        PYTHONPATH = "${WORKSPACE}"
    }
    stages {
        stage('Light Run') {
            steps {
                sh """
                    echo "Executando versão leve do pipeline para o problema: ${params.problem_name}"
                    python3 run_python_script.py pipeline ${params.problem_name} default default default default > light_pipeline.log 2>&1
                    cat light_pipeline.log
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'light_pipeline.log', allowEmptyArchive: true
                }
            }
        }
    }
}