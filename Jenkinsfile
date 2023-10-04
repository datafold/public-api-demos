pipeline {
    agent { dockerfile true }
    options {
        disableConcurrentBuilds()
        ansiColor('xterm')
        timeout(time: 60, unit: 'MINUTES')
        buildDiscarder(logRotator(artifactNumToKeepStr: '30', daysToKeepStr: '35'))
    }
    stages {
        stage('Test') {
            environment {
                DBT_CLOUD_ACCOUNT_ID = "12345"
                DBT_CLOUD_PROJECT_ID = "12345"
                DBT_CLOUD_JOB_ID = "12345" // pull request job ID
                PRODUCTION_JOB_ID = "12345" // production job ID
                DBT_CLOUD_API_TOKEN = credentials('dbt-service-token')
                DATAFOLD_API_KEY = credentials('datafold-service-token')
                ALPHANUMERIC_CHANGE_BRANCH = CHANGE_BRANCH.replaceAll(/[^a-zA-Z\d_]/, '') // Bigquery requirement
            }
            when { not { allOf {
                environment name: "CHANGE_TARGET", value: "master";
                environment name: "CHANGE_BRANCH", value: "integration_test"
                environment name: "CHANGE_BRANCH", value: "integration_test_edw"
            } } }
            steps {
                sh("python3.7 dbt_cloud_ci.py")
                sh("python3.8 datafold_ci.py") // assumes this runs in the dbt project root directory, use python3.8 as 3.7 is not supported anymore
            }
        }
    }
}
