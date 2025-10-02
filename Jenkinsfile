pipeline {
    // 1. Agent Configuration
    // Because the Docker socket is mounted, we can use a simpler agent
    // and execute docker commands directly on the host's Docker daemon.
    agent any

    // 2. Environment Variables
    // Define environment variables for use in the pipeline.
    environment {
        // A unique name and tag for our Docker image.
        IMAGE_NAME = "tastetailor"
        IMAGE_TAG = "${IMAGE_NAME}:${env.BUILD_NUMBER}"
        CONTAINER_NAME = "tastetailor-app"
    }

    // 3. Pipeline Stages
    stages {
        stage('Build Docker Image') {
            steps {
                echo "Building the Docker image: ${env.IMAGE_TAG}"
                // Build the image and tag it for local use.
                sh "docker build -t ${env.IMAGE_TAG} ."
            }
        }

        stage('Run Application Locally') {
            steps {
                echo "Deploying the container to the local machine..."
                // Use the 'withCredentials' block to securely access your .env file content.
                // 'tastetailor-env-file' is the ID you must set in Jenkins > Credentials.
                withCredentials([string(credentialsId: 'tastetailor-env-file', variable: 'DOT_ENV_CONTENT')]) {
                    // Create a temporary .env file in the workspace.
                    sh 'echo "${DOT_ENV_CONTENT}" > .env.tmp'

                    // Stop and remove any old container with the same name.
                    sh "docker stop ${CONTAINER_NAME} || true && docker rm ${CONTAINER_NAME} || true"

                    // Run the new container in detached mode, using the .env file.
                    sh "docker run -d --name ${CONTAINER_NAME} -p 8504:8000 --env-file .env.tmp -v ${pwd()}:/app ${env.IMAGE_TAG}"
                }
            }
        }
    }

    // 4. Post-build Actions
    // Actions that run at the end of the pipeline, regardless of success or failure.
    post {
        always {
            echo "Pipeline finished. Image ${env.IMAGE_TAG} is available locally."
            // Securely clean up the temporary .env file and the workspace.
            sh 'rm -f .env.tmp'
            cleanWs()
        }
    }
}