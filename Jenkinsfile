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

      steps {
            checkout scmGit(
            branches: [[name: 'master']],
            userRemoteConfigs: [[
                url: 'https://github.com/Spokay/Wildlens_CICD.git',
                credentialsId: 'jenkins-spokay-github-credential'
            ]]
            )
            sh 'pwd'
       
            withCredentials([file(credentialsId: 'wildlens_backend_env_file', variable: 'back_env_file')]) {
                sh "cp $back_env_file .env.backend"
                sh 'echo ENVIRONMENT=production >> .env.backend'
            }
            withCredentials([file(credentialsId: 'wildlens_db_env_file', variable: 'db_env_file')]) {
                sh "cp $db_env_file .env.db"
            }
            withCredentials([file(credentialsId: 'wildlens_prediction_env_file', variable: 'prediction_env_file')]) {
                sh "cp $prediction_env_file .env.prediction"
            }
            withCredentials([file(credentialsId: 'wildlens_grafana_env_file', variable: 'grafana_env_file')]) {
                sh "cp $grafana_env_file .env.grafana"
            }

            sh 'cat .env.backend'
            sh 'cat .env.db'
            sh 'cat .env.prediction'
            sh 'cat .env.grafana'
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