
from workflows import Workflow, SubWorkflow, Step, Http, Call
from workflows.standard import SysLog

w = Workflow()
# define subworkflow with name and input parameter. We'll add 2 steps
sub = SubWorkflow('make_get_req', params='[url]')
# The first step is to make request based on url input parameter
sub.add_step(Step('http_get', Http('get', '${url}', result='req_out')))
# Second step is to log response
sub.add_step(Step('log_result', SysLog(json='${req_out}', severity='INFO')))
# add subworkflow to Workflow
w.add_subworkflow(sub)

# add two calls to subworkflow
w.add_step(Step('http_get1', Call(sub, {'url': 'https://www.gcpweekly.com'})))
w.add_step(Step('http_get2', Call(sub, {'url': 'https://www.the-swamp.info'})))

if __name__ == '__main__':
    print(w.to_yaml())
