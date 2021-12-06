
from workflows import Workflow, Step, For, Assign
from workflows.standard import SysLog
from workflows.connectors.bigquery import BigQueryTableData

w = Workflow()

insert_body = {
    'rows': [{'json': '${row}'}]
}

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