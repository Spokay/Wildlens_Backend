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

            sh '''
                ls -la
                
                chmod 755 .
                
                rm -f .env.backend .env.db .env.prediction .env.grafana
            '''
       
            withCredentials([file(credentialsId: 'wildlens_backend_env_file', variable: 'back_env_file')]) {
                script {
                    def back_env_file = readFile(back_env_file)
                    writeFile file: '.env.backend', text: back_env_file + '\nENVIRONMENT=production'
                }
            }
            withCredentials([file(credentialsId: 'wildlens_db_env_file', variable: 'db_env_file')]) {
                script {
                    def db_env_file = readFile(db_env_file)
                    writeFile file: '.env.db', text: db_env_file
                }
            }
            withCredentials([file(credentialsId: 'wildlens_prediction_env_file', variable: 'prediction_env_file')]) {
                script {
                    def prediction_env_file = readFile(prediction_env_file)
                    writeFile file: '.env.prediction', text: prediction_env_file
                }
            }
            withCredentials([file(credentialsId: 'wildlens_grafana_env_file', variable: 'grafana_env_file')]) {
                script {
                    def grafana_env_file = readFile(grafana_env_file)
                    writeFile file: '.env.grafana', text: grafana_env_file
                }
            }
            sh 'chmod 644 .env.backend .env.db .env.prediction .env.grafana'
            script {
                docker.withRegistry('https://registry.spokayhub.top', 'spokayhub-registry-credentials') {
                    sh 'docker compose pull'
                    sh 'docker compose down'
                    sh 'docker compose up -d wildlens_backend'
                }
            }
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