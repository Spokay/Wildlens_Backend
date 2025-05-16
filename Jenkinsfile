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
        sh 'sh \'python -m venv ${WORKSPACE}/venv\''
        sh ' sh \'. ${WORKSPACE}/venv/bin/activate && pip install -r requirements.txt\''
      }
    }

    stage('Run tests') {
      steps {
        script {
          sh 'pytest --cov=app --cov-report=xml --junitxml=test-results.xml'
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