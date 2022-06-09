import json
import os
import sys
from pathlib import Path

from cumulusci.tasks.bulkdata import LoadData
from cumulusci.tasks.salesforce import BaseSalesforceApiTask

class TriggerRafi(BaseSalesforceApiTask):
    task_docs = """
    Use the `cucumber_filter_tags` option to specify the Cucumber Feature File Path which contains the tests.
    Use the `api` option to specify the api version.
    Use 'browser' option to specify the Browser for test execution.
    Use 'pod' to specify the Instance name for execution (eg. GS0).
    Use 'url' to specify the instance URL for test execution.
    Use 'username' to specify the Username for login to Org.
    Use 'password'  to specify the Password for login to Org.
    User 'rafi_env' to specify the DataPy environment path where scripts with run (optional)
    """

    task_options = {
    "cucumber_filter_tags": {
        "description": "Feature file having cucumber tests.",
        "required": True,
    },
    "api": {
        "description": "API version.",
        "required": True,
    },
    "browser": {
        "description": "Browser where the tests will get executed",
        "required": True,
    },
    "pod": {
        "description": "Pod name where the Org is present",
        "required": True,
    },
    "url": {
        "description": "URL of the org",
        "required": True,
    },
    "username": {
        "description": "Username for the Org where script need to be triggered",
        "required": False,
    },
    "password": {
        "description": "Password for the Org where script need to be triggered",
        "required": False,
    },
    "rafi_env": {
        "description": "RAFI environment Path",
        "required": False,
    },
    **LoadData.task_options,
    }

    rafi_env_path = "/Users/ankita.tiwari/Documents/SourceCode/RAFI/Sanity/Industries-automation"

    def _init_options(self, kwargs):
        super()._init_options(kwargs)

        if self.options.get("rafi_env") is not None:
            self.rafi_env_path = self.options.get("rafi_env")

        print(self.rafi_env_path)

# mvn -pl Core,FinancialServicesCloud test -Djenkins=false -Dplatform=Linux -Dbrowser=chrome -Dtimestamp=1621352332 -DrestApiVersion=54.0 -DsoapApiVersion=54.0 -DenvUrl=https://login.salesforce.com -DorgUser=sp_test1@fsc.cumulusci.org -DorgPassword=testuser01 -Dpod=GS0 -Dcucumber.options=“src/test/resources/features/FHIRCommunityScenarios.feature” -Dproxy=false -DreleaseVersion= -Ddebug=false

    def _run_task(self):
        cucumber_filter_tags = self.options.get("cucumber_filter_tags")
        api_version = self.options.get("api")
        browser = self.options.get("browser")
        pod = self.options.get("pod")
        url = self.options.get("url")
        username = self.options.get("username")
        password = self.options.get("password")

        print("INPUT:")
        print(
            "Cucumber filter tag - " + cucumber_filter_tags,
            "\nApi version - " + str(api_version),
            "\nBrowser - " + browser,
            "\nPod for Test Execution - " + pod,
            "\nURL of Org - " + url,
            "\nUsername - " + username,
            "\nPassword - " + password,
            )

        execution_command = (
                "cd " + str(self.rafi_env_path) + ";mvn -pl Core,FinancialServicesCloud test"
                                                  " -Djenkins=false -Dplatform=Linux -Dbrowser="
                + str(browser)
                + " -Dtimestamp=1621352332"
                  " -DrestApiVersion="
                + str(api_version)
                + " -DsoapApiVersion="
                + str(api_version)
                + " -DenvUrl="
                + str(url)
                + " -DorgUser="
                + str(username)
                + " -DorgPassword="
                + str(password)
                + " -Dpod="
                + str(pod)
                + " -Dcucumber.filter.tags=@"
                + str(cucumber_filter_tags)
                + " -Dproxy=false -DreleaseVersion= -Ddebug=false" ":mvn -pl Core,TestReport test -Dbrowser=chrome"
                + ";cd /Users/ankita.tiwari/Documents/SourceCode/CumulusCI/Demo"
                + ";sh SanityReport.sh"
        )

        print(execution_command)


        os.system("echo 'Running RAFI Tests'")
        os.system(execution_command)

        return "RAFI Test Execution Completed Successfully"