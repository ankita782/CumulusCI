import json
import os
import sys
from pathlib import Path
from cumulusci.tasks.bulkdata import LoadData
from cumulusci.tasks.salesforce import BaseSalesforceApiTask
class LoadFromDatapy(BaseSalesforceApiTask):
    username = "sp_test1@fsc.cumulusci.org"
    password = "testuser01"
    task_docs = """
    Use the `config` option to specify the Config File Path which contains the script.
    Use the `api` option to specify the api version.
    Use 'service_context' option to specify the Service Context File Path which contains Org details.
    Use 'mode' to specify the mode of execution.
    User 'datapy_env' to specify the DataPy environment path where scripts with run (optional)
    """
    task_options = {
        "config": {
            "description": "Config file path for executing DataPy tests.",
            "required": True,
        },
        "api": {
            "description": "API version.",
            "required": True,
        },
        "service_context": {
            "description": "Service context file for the execution properties.",
            "required": True,
        },
        "mode": {
            "description": "Execution mode.",
            "required": True,
        },
        "datapy_env": {
            "description": "DataPy environment Path",
            "required": False,
        },
        "username": {
            "description": "Username for the Org where script need to be triggered",
            "required": False,
        },
        "password": {
            "description": "Password for the Org where script need to be triggered",
            "required": False,
        },
        **LoadData.task_options,
    }
    datapy_env_path = "/Users/ankita.tiwari/Documents/SourceCode/238/Hc-Learning-TCRM/DataPy"
    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        if self.options.get("datapy_env") is not None:
            self.datapy_env_path = self.options.get("datapy_env")
        print(self.datapy_env_path)
        if self.options.get("username") is not None:
            self.username = self.options.get("username")

        if self.options.get("password") is not None:
            self.password = self.options.get("password")
        service_context_file_path = (
                str(self.datapy_env_path)
                + "/configs/serviceContext/"
                + str(self.options.get("service_context"))
        )
        # read service context file to update Org username and password
        service_context_json_file = open(service_context_file_path, "r")
        data = json.load(service_context_json_file)
        service_context_json_file.close()
        # modify username and password in buffered content
        data["username"] = self.username
        data["password"] = self.password
        print("SERVICE CONTEXT:")
        print(data)
        # save changes to service context json file
        service_context_json_file = open(service_context_file_path, "w+")
        service_context_json_file.write(json.dumps(data))
        service_context_json_file.close()
        # ./runner.sh --config configs/Insurance/TCRM_Analytics/create_claim/base_scenario_vlocity_Temp1.json --api 54.0 --serviceContext vlocity_spec.json --mode scenario
    def _run_task(self):
        datapy_config = self.options.get("config")
        api_version = self.options.get("api")
        service_context = self.options.get("service_context")
        mode = self.options.get("mode")
        print("INPUT:")
        print(
            "Config File - " + str(datapy_config),
            "\nApi version - " + str(api_version),
            "\nService Context File - " + str(service_context),
            "\nMode of Execution - " + str(mode),
            )
        execution_command = (
                "cd "
                + str(self.datapy_env_path)
                + ";./runner.sh --config "
                + str(datapy_config)
                + " --api "
                + str(api_version)
                + " --serviceContext "
                + str(service_context)
                + " --mode "
                + str(mode)
        )
        # execution_command = "cd /Users/ankita.tiwari/SourceCode/forked-DataPy/DataPy;./runner.sh --config configs/Insurance/TCRM_Analytics/update_account_billing.json --api 54.0 --serviceContext vlocity_spec.json --mode scenario"
        os.system("echo 'Running DataPy'")
        os.system(execution_command)
        return "DataPy Execution Completed Successfully"