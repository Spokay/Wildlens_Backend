pipeline {
    agent {
        label 'python-3-12'
    }

    environment {
      ENVIRONNEMENT='testing'
    }
    
    stages {
      stage('Checkout') {
            steps {
                checkout scm
            }
      }
        
      stage('Setup Virtual Environment') {
        steps {
            sh '''
                rm -rf venv || true
                
                python3 -m venv venv
                
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                
                pip install pytest pytest-cov
            '''
        }
      }
      
              
      stage('Test') {
        steps {
            sh '''
                . venv/bin/activate
                
                python3 -m pytest
            '''
        }
      }
      
      stage('Build') {
        steps {
            sh '''
                echo "Building application..."
            '''
        }
      }
      
      stage('Deploy') {
        when {
            branch 'master'
        }
        steps {
            sh '''
                echo "Deploying to production environment..."
            '''
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
