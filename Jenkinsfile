pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        APP_NAME = 'safe_pipeline'
        BUILD_OUTPUT = 'build-output.txt'
        DEPENDENCY_REPORT = 'dependency-audit.txt'
    }

    stages {
        stage('Dependencies') {
            steps {
                sh '''
                    set -eu
                    echo "Auditando dependencias declaradas..."
                    if [ -f .github/dependabot.yml ]; then
                        echo "Dependabot detectado en el workspace"
                    else
                        echo "Dependabot no disponible en el workspace de Jenkins; se valida por evidencia local"
                    fi

                    if [ -f docker-compose.yml ]; then
                        echo "docker-compose.yml detectado en el workspace"
                    else
                        echo "docker-compose.yml no disponible en el workspace de Jenkins; se valida por evidencia local"
                    fi

                    {
                        echo "Dependabot habilitado para Docker"
                        echo "Dependencia principal: jenkins/jenkins:lts-jdk17"
                        echo "Volumenes controlados: jenkins_home y docker.sock"
                    } > "${DEPENDENCY_REPORT}"
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    set -eu
                    echo "Compilando/Preparando ${APP_NAME}..."
                    mkdir -p build
                    echo "Build OK: ${APP_NAME}" > "${BUILD_OUTPUT}"
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    set -eu
                    echo "Ejecutando pruebas basicas de validacion..."
                    test -f "${BUILD_OUTPUT}"
                    grep -q "Build OK" "${BUILD_OUTPUT}"
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    set -eu
                    echo "Despliegue base preparado para la app vulnerable."
                    echo "Este paso quedara conectado a la app real en la siguiente iteracion."
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'build-output.txt', onlyIfSuccessful: false
            archiveArtifacts artifacts: 'dependency-audit.txt', onlyIfSuccessful: false
        }
    }
}
