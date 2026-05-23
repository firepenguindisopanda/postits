pipeline {
    agent any

    environment {
        PRODUCTION_DIR = "/home/swepi/Desktop/FastAPIStarter-main"
        VENV_DIR       = "${WORKSPACE}/venv"
    }

    stages {
        stage('Setup') {
            steps {
                sh """
                    python3 -m venv ${VENV_DIR}
                    ${VENV_DIR}/bin/pip install --upgrade pip
                    ${VENV_DIR}/bin/pip install -e .
                """
            }
        }

        stage('Lint') {
            steps {
                sh "${VENV_DIR}/bin/ruff check ."
            }
        }

        stage('Test') {
            steps {
                sh "${VENV_DIR}/bin/pytest --tb=short -v"
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh """
                    rsync -av --delete \
                        --exclude='venv/' \
                        --exclude='.env' \
                        --exclude='__pycache__/' \
                        --exclude='*.pyc' \
                        --exclude='*.db' \
                        --exclude='.ruff_cache/' \
                        --exclude='.git/' \
                        --exclude='project_starter.egg-info/' \
                        ./ ${PRODUCTION_DIR}/
                    ${PRODUCTION_DIR}/venv/bin/pip install -e ${PRODUCTION_DIR}
                    sudo /usr/bin/systemctl restart fastapi-app
                """
            }
        }
    }

    post {
        failure {
            echo "Pipeline failed. Check the logs for details."
        }
    }
}
