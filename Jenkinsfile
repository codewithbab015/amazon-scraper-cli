pipeline {
    agent any

    environment {
        GIT_URL = 'https://github.com/baloyi015/amazon-scraper-vi.git'
        GIT_CREDENTIALS_ID = 'github_token_id'
        PIP_CACHE_DIR = "${WORKSPACE}/.pip_cache"
        VENV_DIR = "${WORKSPACE}/.venv"
        RUN_NAME = "pet-dry-food"
        RUN_MODE = "detail"
        DOCKERHUB_CREDENTIALS_ID = 'docker_token_id'
    }

    stages {
        stage('Initialize SCM') {
            steps {
                checkout scmGit(
                    branches: [[name: '*/main']],
                    extensions: [],
                    userRemoteConfigs: [[
                        credentialsId: "${env.GIT_CREDENTIALS_ID}",
                        url: "${env.GIT_URL}"
                    ]]
                )
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    #!/bin/bash
                    set -e
                    chmod +x activate_venv_ci.sh
                    ./activate_venv_ci.sh
                '''
            }
        }

        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${env.DOCKERHUB_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                    '''
                }
            }
        }

        stage('Pull Docker Image') {
            steps {
                sh '''
                    #!/bin/bash
                    set -e
                    docker pull mrbaloyin/etl-amazon-scraper-v1:latest
                    docker images
                '''
            }
        }

        stage('Run Mode: Main') {
            when {
                expression { env.RUN_MODE == 'main' } 
            }
            steps {
                sh '''
                    #!/bin/bash
                    set -e
                    mkdir -p data
                    docker run -v "${PWD}/data":/app/data/ mrbaloyin/etl-amazon-scraper-v1:latest \
                        --run_name "${RUN_NAME}" \
                        --run_mode "${RUN_MODE}"
                '''
            }
        }


        stage('Run Mode: Detail'){
            when {
                expression { env.RUN_MODE == 'detail' } 
            }
            steps {
                sh '''
                    #!/bin/bash
                    set -e
                    mkdir -p data
                    docker run -v "${PWD}/data":/app/data/ mrbaloyin/etl-amazon-scraper-v1:latest \
                        --run_name "${RUN_NAME}" \
                        --run_mode "${RUN_MODE}"
                '''
            }
        }



        stage('Completed') {
            steps {
                echo 'All stages completed successfully.'
                echo 'You can now access the results in the workspace.'
                sh '''
                    #!/bin/bash
                    set -e
                    ls -lh
                '''
            }
        }
    }

    post {
        always {
            echo 'Archiving pip cache directory for reuse...'
            archiveArtifacts artifacts: '.pip_cache/**', fingerprint: true
        }
    }
}

        // stage('Run Mode: Detail') {
        //     when {
        //         expression { env.RUN_MODE == 'detail' } 
        //     }

        //     steps {
        //         sh '''#!/bin/bash
        //             set -e
        //             source "$VENV_DIR/bin/activate"
        //             python3 run_script.py \
        //                 --run_name "$RUN_NAME" \
        //                 --run_type "detail"
        //         '''
        //     }
        // }

        // stage('Run Mode: Clean') {
        //      when {
        //         expression { env.RUN_MODE == 'clean' } 
        //     }
            
        //     steps {
        //         sh '''#!/bin/bash
        //             set -e
        //             source "$VENV_DIR/bin/activate"
        //             python3 run_script.py \
        //                 --run_name "$RUN_NAME" \
        //                 --run_type "clean"
        //         '''
        //     }
        // }

        // stage('Data Modeler Runner') {
        //     steps {
        //         sh '''#!/bin/bash
        //             set -e
        //             source "$VENV_DIR/bin/activate"
        //             python3 data_moder.py
        //         '''
        //     }
        // }

        // stage('Data Processor Runner') {
        //     steps {
        //         sh '''#!/bin/bash
        //             set -e
        //             source "$VENV_DIR/bin/activate"
        //             python3 data_processor.py
        //         '''
        //     }
        // }
