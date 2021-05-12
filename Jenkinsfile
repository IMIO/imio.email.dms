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
        echo "to do (call rundeck)"
      }
    }
    stage('Deploy') {
        agent any
        when {
          buildingTag()
				}
        steps {
          echo 'Deploying only because this commit is tagged.'
          echo "Branch: $BRANCH_NAME"
          echo "Tag: $TAG_NAME"
          moveImageToProdRegistry(env.TAG_NAME, "iadocs/dms/mail")
          echo "Schedule Rundeck job"
          echo "curl -XPOST -H \"x-Rundeck-Auth-Token:$RUNDECK_TOKEN\" https://run.imio.be/api/24/job/000/run"
					mail to: "support-docs+jenkins@imio.be",
             subject: "New release deployed: ${currentBuild.displayName}",
             body: "The pipeline ${env.JOB_NAME} ${env.BUILD_NUMBER} released ${env.fullDisplayName}"
          echo 'Upgrade finished.'
			}
		}
  }
  post {
      fixed{
        mail to: "support-docs+jenkins@imio.be",
          subject: "Fixed Pipeline: ${currentBuild.fullDisplayName}",
          body: "The pipeline ${env.JOB_NAME} ${env.BUILD_NUMBER} is back to normal (${env.BUILD_URL})"
      }
      failure{
        mail to: "support-docs+jenkins@imio.be",
          subject: "Failed Pipeline: ${currentBuild.fullDisplayName}",
          body: "The pipeline ${env.JOB_NAME} ${env.BUILD_NUMBER} failed (${env.BUILD_URL})"
      }
      always {
        node(null)  {
					deleteDir()
        }
      }
    }
}
