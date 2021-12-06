from workflows import Workflow, Step, Return, Switch, Condition, Assign
from workflows.standard import SysSleep, SysLog
from workflows.connectors.vision import Vision

w = Workflow(params=['input'])

w.add_step(Step('log_input', SysLog(json='${input}')))
w.add_step(Step('assign_variables', Assign(variables={'gcs_input_path': '${input.gcs_input_path}',
                                                      'gcs_output_path': '${input.gcs_output_path}'})))

# request for Cloud Vision with variable references
input_data = {
    "requests": [
        {
            "inputConfig": {
                "gcsSource": {
                    "uri": '${gcs_input_path}'
                },
                "mimeType": "application/pdf"
            },
            "features": [{
                "type": "DOCUMENT_TEXT_DETECTION"
            }],
            "outputConfig": {
                "gcsDestination": {
                    "uri": '${gcs_output_path}'
                }
            }
        }
    ]
}

# using Result
ocr_res = Result('ocr_res')
# submit job
ocr_step = Step('vision_ocr', Vision.asyncBatchAnnotate(input_data), ocr_res)

# get job status
ocr_status = Step('get_vision_result', Vision.getJob('ocr_res.body.name', 'ocr_status'))

w.add_step(ocr_step)

# Sleep
wait_step = Step('wait_step', SysSleep(2))
w.add_step(wait_step)
w.add_step(ocr_status)

# final step, which returns result
step_end = Step('end_step', Return('ocr_status'))

# checking results, in next_ we're referencing step variable names instead of using string
check_status = Step('check_status', Switch([
    Condition('${ocr_status.body.metadata.state!="DONE"}', next_=wait_step),
    Condition('${ocr_status.body.metadata.state=="DONE"}', next_=step_end)
]))

w.add_step(check_status)

w.add_step(step_end)

if __name__ == '__main__':
    print(w.to_yaml())
