from workflows import Workflow, Step, Assign, Return
from workflows.standard import SysLog
from workflows.connectors.firestore import Firestore

bucket_name = 'f2b-exports'

w = Workflow()
step = Step('asign_variables', Assign(variables={'bucket': bucket_name,
                                                 'project': '${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}'}))
w.add_step(step)

output_path = f'${{"gs://{bucket_name}/export_" + string(sys.now())}}'

step1 = Step('firestore_export', Firestore.exportDocuments('project', ['sessions'], output_path, result='export_job'))

w.add_step(step1)
w.add_step(Step('log_result', SysLog(json='${export_job}')))
w.add_step(Step('return_res', Return('export_job')))

if __name__ == '__main__':
    print(w.to_yaml())
