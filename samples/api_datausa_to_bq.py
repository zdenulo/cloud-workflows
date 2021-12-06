"""
Example of fetching data from an api and inserting to BigQuery. Before that it creates table in BQ by calling
sub_workflow which is imported from another workflow

BigQuery dataset needs to exists.
This example with input parameters
{
"dataset":"data",
"table":"usa_population"
}
Because of current memory limitations in Cloud Workflows, rows are inserted into BigQuery one by one, not all in single
request, which is not most efficient way...
"""
from workflows import Workflow, Step, Http, Assign, For, Call
from workflows.standard import SysLog
from workflows.connectors.bigquery import BigQueryTableData
from bq_create_table import w as w_create_bq_table

w = Workflow(params='[args]')
w_create_bq_table.name = 'sub_create_bq_table'  # change the name of the workflow, because workflow is 'main'
w.add_subworkflow(w_create_bq_table)
# set variables
w.add_step(Step('assign_variables', Assign(variables=[
    {'bq_dataset': '${args.dataset}'},
    {'bq_table': '${args.table}'},
    {'gcp_project': '${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}'}
],
)))
# call included sub_workflow and pass arguments
w.add_step(
    Step('create_bq_table',
         Call(w_create_bq_table.name, args={
             'dataset': '${bq_dataset}',
             'table': '${bq_table}'
         }
              )))
# get data from API with query params and output to result
w.add_step(Step('get_data', Http('get', 'https://datausa.io/api/data', query={'drilldowns': 'State',
                                                                              'measures': 'Population'},
                                 result='api_res')))

w.add_step(Step('api_log', SysLog(json='${api_res}')))

# body for BigQuery insert
insert_body = {
    'rows': [{'json': '${row}'}]
}
# loop through data, get desired fields into variable, insert row in BigQuery and log response
w.add_step(Step('extract_data',
                For(list_values='${api_res.body.data}',  # here is list from API response
                    loop_variable='item',  # variable name in loop step
                    steps=[  # steps to execute
                        # prepare row, get desired data
                        Step('set_row', Assign(variables=[
                            {'row':
                                 {'State': '${item.State}',
                                  'Year': '${item.Year}',
                                  'Population': '${item.Population}',
                                  }
                             },
                        ]
                        )),
                        # make BigQuery request
                        Step('insert_bq',
                             BigQueryTableData.insertAll('${gcp_project}', '${bq_dataset}', '${bq_table}', insert_body,
                                                         'bq_insert')),
                        # log response
                        Step('log_item', SysLog(json='${bq_insert}', severity='INFO'))
                    ])))

if __name__ == '__main__':
    print(w.to_yaml())
