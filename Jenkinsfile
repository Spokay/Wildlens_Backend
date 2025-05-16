pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                sh '''
                    # Supprimer l'environnement virtuel s'il existe
                    rm -rf venv || true
                    
                    # Créer un nouvel environnement virtuel
                    python3 -m venv venv
                    
                    # Activer l'environnement et installer les dépendances
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    # S'assurer que pytest et pytest-cov sont installés
                    pip install pytest pytest-cov
                '''
            }
        }
        
               
        stage('Test') {
            steps {
                sh '''
                    . venv/bin/activate
                    
                    # Vérifier que pytest-cov est installé
                    pip list | grep pytest-cov
                    
                    # Exécuter les tests avec couverture
                    python -m pytest tests/
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                    cobertura coberturaReportFile: 'coverage.xml'
                }
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
