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
        checkout scmGit(
          branches: [[name: 'master']],
          userRemoteConfigs: [
            [
              url: 'https://github.com/WildLens/Wildlens_CICD.git'
            ]
          ]
        )
        sh 'pwd'
      }
      steps {
        sh "pwd"
        withCredentials([string(credentialsId: 'wildlens_backend_env_file', variable: 'back_env_file')]) {
            sh 'echo $back_env_file > .env.backend'
        }
        withCredentials([string(credentialsId: 'wildlens_db_env_file', variable: 'db_env_file')]) {
            sh 'echo $db_env_file > .env.db'
        }
        withCredentials([string(credentialsId: 'wildlens_prediction_env_file', variable: 'prediction_env_file')]) {
            sh 'echo $prediction_env_file > .env.prediction'
        }
        withCredentials([string(credentialsId: 'wildlens_grafana_env_file', variable: 'grafana_env_file')]) {
            sh 'echo $grafana_env_file > .env.grafana'
        }

        sh "cat .env.backend"
        sh "cat .env.db"
        sh "cat .env.prediction"
        sh "cat .env.grafana"
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