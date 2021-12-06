"""
Example of using Workflows to start Cloud SQL instance then waits and stops instance.
Can be used for periodical start/stop for dev instances
"""

from workflows import Workflow, Step, Assign, Return
from workflows.connectors.sql import SQLInstances
from workflows.standard import SysLog, SysSleep

sleep_time = 60*60*8  # number of seconds between start and stop steps

w = Workflow()

w.add_step(Step('assign_variables', Assign(variables=[
    {'gcp_project': '${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}'},
    {'sql_instance': 'my-instance'}  # name of the Cloud SQL instance
])))

# get meta data for instance
w.add_step(Step('get_sql_instance', SQLInstances.get('${gcp_project}', '${sql_instance}',
                                                     result='sql_info')))

# assigning result to variable and then updating to start instance
w.add_step(Step('change_settings', Assign(variables=[
    {'sql_info2': '${sql_info}'},
    {'sql_info2.settings.activationPolicy': 'ALWAYS'}
])))
w.add_step(Step('start_sql_instance', SQLInstances.update('${gcp_project}', '${sql_instance}', '${sql_info2}',
                                                          result='sql_start_res')))
w.add_step(Step('log_start', SysLog(json='${sql_start_res}')))

# sleep step
w.add_step(Step('sleep_step', SysSleep(sleep_time)))

# before stopping get the latest info which will be updated
w.add_step(Step('get_sql_instance2', SQLInstances.get('${gcp_project}', '${sql_instance}',
                                                      result='sql_info_run')))
w.add_step(Step('change_settings2', Assign(variables=[
    {'sql_info_stop': '${sql_info_run}'},
    {'sql_info_stop.settings.activationPolicy': 'NEVER'}
])))
w.add_step(Step('stop_sql_instance', SQLInstances.update('${gcp_project}', '${sql_instance}', '${sql_info_stop}',
                                                         result='sql_stop_res')))
w.add_step(Step('log_stop', SysLog(json='${sql_stop_res}')))

if __name__ == '__main__':
    print(w.to_yaml())
