pipeline {
  agent {
    docker {
      image 'python:3.11.0'
      args '-v /tmp:/tmp'
    }

  }
  stages {
    stage('Install dependencies') {
      steps {
        script {
          sh '''
# Création et activation de l'environnement virtuel
python -m venv ${WORKSPACE}/venv
. ${WORKSPACE}/venv/bin/activate

# Installation des dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Exécution des tests
python -m pytest --cov=app --cov-report=xml --junitxml=test-results.xml
'''
        }

      }
    }

    stage('Run tests') {
      steps {
        script {
          sh 'python3 -m pytest --cov=app --cov-report=xml --junitxml=test-results.xml'
        }

        post() {
          always() {
            junit 'test-results.xml'
            cobertura(coberturaReportFile: 'coverage.xml')
          }

        }

      }
    }

    stage('Build') {
      steps {
        script {
          sh 'echo "Building the application..."'
        }

      }
    }

  }
  environment {
    PYTHONPATH = "${WORKSPACE}"
  }
  post {
    success {
      echo 'Pipeline executed successfully!'
    }

    failure {
      echo 'Pipeline execution failed!'
    }

    always {
      sh 'echo "Cleaning up..."'
    }

  }
}