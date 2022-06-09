from cumulusci.tasks.bulkdata.load_from_datapy import LoadFromDatapy

bulkgen_task = "cumulusci.tasks.bulkdata.load_from_datapy.LoadFromDatapy"


# Class to glue together the task_options from LoadDataFromDatapy and LoadFromDatapy
class LoadDataFromDatapy(LoadFromDatapy):
    """Load data from DataPy"""

    task_options = {
        **LoadFromDatapy.task_options
    }

    def _init_options(self, kwargs):
        args = {"data_generation_task": bulkgen_task, **kwargs}
        super()._init_options(args)