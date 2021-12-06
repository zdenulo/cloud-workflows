"""
Example of creating BigQuery table with TryExceptRetry
"""

from workflows import Workflow, Step, Assign, Return, TryExceptRetry
from workflows.standard import SysLog
from workflows.connectors.bigquery import BigQueryTables

w = Workflow(params='[dataset, table]')

w.add_step(Step('assign_variables', Assign(variables=[
    {'bq_dataset': '${dataset}'},
    {'bq_table': '${table}'},
    {'gcp_project': '${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}'}]
)))

bq_table_reference = {
    "tableReference": {
        "projectId": '${gcp_project}',
        "datasetId": '${bq_dataset}',
        "tableId": '${bq_table}'
    },
    "schema": {
        "fields": [
            {"name": "State", "type": "STRING"},
            {"name": "Year", "type": "STRING"},
            {"name": "Population", "type": "INTEGER"}
        ]
    }
}

create_bq_table_step = Step('create_bq_table_req',
                            BigQueryTables.insert('${bq_dataset}', '${gcp_project}', bq_table_reference,
                                                  result='bq_response'))
w.add_step(Step('create_bq_table',
                TryExceptRetry([create_bq_table_step,
                                Step('log_response', SysLog(json='${bq_response}')),
                                Step('output', Return('${bq_response}'))
                                ],
                               as_='e',
                               except_steps=[
                                   Step('known_errors', SysLog(json='${e}')),
                               ])
                )
           )

if __name__ == '__main__':
    print(w.to_yaml())
