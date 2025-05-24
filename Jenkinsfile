pipeline {
  agent any
  stages {
    stage('Testing') {
      agent {
        node {
          label 'python-3-12'
        }

      }
      environment {
        ENVIRONMENT = 'testing'
      }
      steps {
        checkout scm
        sh '''
                rm -rf venv || true
                
                python3 -m venv venv
                
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                
                pip install pytest pytest-cov'''
        sh '''
                . venv/bin/activate
                
                python3 -m pytest'''
      }
    }

    stage('Deployment') {
      environment {
        ENVIRONMENT = 'production'
      }
      steps {
        sh 'docker ps -a'
      }
    }

  }
  post {
    success {
      echo 'Pipeline executed successfully!'
    }

    failure {
      echo 'Pipeline execution failed!'
    }

    always {
      echo 'Cleaning up...'
    }

  }
}