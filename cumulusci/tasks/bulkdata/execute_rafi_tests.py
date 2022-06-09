from cumulusci.tasks.bulkdata.trigger_rafi import TriggerRafi

bulkgen_task = "cumulusci.tasks.bulkdata.trigger_rafi.TriggerRafi"


# Class to glue together the task_options from ExecuteRafi and TriggerRafi
class ExecuteRafi(TriggerRafi):
    """Trigger RAFI Tests"""

    task_options = {**TriggerRafi.task_options}

    def _init_options(self, kwargs):
        args = {"data_generation_task": bulkgen_task, **kwargs}
        super()._init_options(args)