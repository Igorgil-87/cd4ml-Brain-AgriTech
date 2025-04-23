pipeline {
    agent any
    parameters {
        choice(name: 'problem_name', choices: ['rendimento', 'insumo',  'saude_lavoura','commodities'], 
               description: 'Choose the problem name')
        string(name: 'ml_pipeline_params_name', defaultValue: 'default', description: 'Specify the ml_pipeline_params file')
        string(name: 'feature_set_name', defaultValue: 'default', description: 'Specify the feature_set name/file')
        string(name: 'algorithm_name', defaultValue: 'default', description: 'Specify the algorithm (overrides problem_params)')
        string(name: 'algorithm_params_name', defaultValue: 'default', description: 'Specify the algorithm params')
    }
    triggers {
        pollSCM('* * * * *') // Poll SCM every minute for new changes
    }
    options {
        timestamps() // Add timestamps to output
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
                    sh '''
                    set -e  # Encerra o script em caso de erro

                    echo "=== Configuração Inicial ==="
                    CACHE_DIR="/tmp/pip-cache"
                    LOG_FILE="test_execution.log"
                    TEST_DIR="cd4ml/problems/rendimento/tests"
                    RETRY_COUNT=3

                    echo "=== Configurando cache de pacotes ==="
                    mkdir -p ${CACHE_DIR}

                    echo "=== Instalando dependências com retry ==="
                    for i in $(seq 1 ${RETRY_COUNT}); do
                        pip3 install --cache-dir=${CACHE_DIR} --upgrade pip > ${LOG_FILE} 2>&1
                        pip3 install --cache-dir=${CACHE_DIR} 'numpy>=1.22.0,<1.26.0' 'pandas>=1.5.0,<1.6.0' 'mlflow==2.1.1' 'scipy>=1.9.0,<1.11.0' 'pytest==7.2.1' 'requests-mock==1.10.0' >> ${LOG_FILE} 2>&1
                        if [ $? -eq 0 ]; then
                            echo "Instalação concluída com sucesso!"
                            break
                        fi
                        echo "Tentativa ${i} falhou. Retentando..."
                        if [ $i -eq ${RETRY_COUNT} ]; then
                            echo "Falha na instalação após ${RETRY_COUNT} tentativas."
                            cat ${LOG_FILE}
                            exit 1
                        fi
                    done

                    echo "=== Listando pacotes instalados ==="
                    pip3 freeze | tee -a ${LOG_FILE}

                    echo "=== Executando pytest nos testes em ${TEST_DIR} ==="
                    pytest ${TEST_DIR} --maxfail=2 --disable-warnings --tb=short | tee -a ${LOG_FILE}

                    echo "=== Testes concluídos com sucesso! ==="
                    '''
                }
            }
        }

        stage('Run ML pipeline') {
           steps {
               sh 'python3 run_python_script.py pipeline ${problem_name} ${ml_pipeline_params_name} ${feature_set_name} ${algorithm_name} ${algorithm_params_name} > pipeline.log 2>&1'
               sh 'cat pipeline.log' // Exibe o conteúdo do log após a execução
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
                    not { equals expected: 'default', actual: "${params.feature_set_name}"}
                    not { equals expected: 'default', actual: "${params.algorithm_name}"}
                    not { equals expected: 'default', actual: "${params.algorithm_params_name}"}
               }
           }
           steps {
                sh '''
                set +e
                python3 run_python_script.py acceptance
                set -e
                '''
                sh 'python3 run_python_script.py register_model ${MLFLOW_TRACKING_URL} no'
           }
       }
       stage('Deploy Model') {
           steps {
               script {
                   def production_model_id = sh(script: 'python3 scripts/check_mlflow_production.py', returnStdout: true).trim()
                   if (production_model_id) {
                       echo "New production model found: ${production_model_id}. Restarting 'model' container..."
                       sh 'docker restart model'
                   } else {
                       echo "No new production model found. Skipping deploy."
                   }
               }
           }
       }
    }
}