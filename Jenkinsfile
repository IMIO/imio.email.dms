@Library('jenkins-pipeline-scripts') _

pipeline {
  agent none
  options {
    buildDiscarder(logRotator(numToKeepStr:'50'))
  }
  stages {
    stage('Build') {

      agent any
        when {
          allOf{
            branch "master"
              not {
                changelog '.*\\[(ci)?\\-?\\s?skip\\-?\\s?(ci)?\\].*'
              }
            not {
              changelog '^Back to development:*'
            }
            not {
              changelog '^Preparing release *'
            }
          }
        }
      steps {
        sh 'make docker-image'
      }
    }
    stage('Push image to staging registry') {
      agent any
        when {
          allOf{
            branch "master"
              not {
                changelog '.*\\[(ci)?\\-?\\s?skip\\-?\\s?(ci)?\\].*'
              }
            not {
              changelog '^Back to development:*'
            }
            not {
              changelog '^Preparing release *'
            }
          }
        }
      steps {
        pushImageToRegistry (
          "${env.BUILD_ID}",
          "iadocs/dms/mail"
        )
      }
    }

    stage('Deploy to staging') {
      agent any
        when {
          allOf {
            branch "master"
              expression {
                currentBuild.result == null || currentBuild.result == 'SUCCESS'
              }
            not {
              changelog '.*\\[(ci)?\\-?\\s?skip\\-?\\s?(ci)?\\].*'
            }
            not {
              changelog '^Back to development:*'
            }
            not {
              changelog '^Preparing release *'
            }
          }
        }
      steps {
        echo "to do"
      }
    }
  }
}
