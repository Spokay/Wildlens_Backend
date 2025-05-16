pipeline {
    agent {
        docker {
            image 'python:3.11.0'
            args '-v /tmp:/tmp'
        }
    }
    
    environment {
        PYTHONPATH = "${WORKSPACE}"
    }

    stages {
      stage("Install dependencies") {
        steps {
          script {
            sh 'pip install -r requirements.txt'
          }
        }
      }

      stage("Run tests") {
        steps {
          script {
            sh 'pytest --cov=app --cov-report=xml --junitxml=test-results.xml'
          }
          post {
            always {
              junit 'test-results.xml'
              cobertura coberturaReportFile: 'coverage.xml'
            }
          }
        }
      }

      stage("Build") {
          steps {
              script {
                  sh 'echo "Building the application..."'            
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
            sh 'echo "Cleaning up..."'
        }
    }
}

