
from workflows import Workflow, Step, Call, Return

w = Workflow()

step_1 = Step('http_request_example',
              Call('http.get', {'url': 'https://www.gcpweekly.com/'}, 'request_result'),
              )

w.add_step(step_1)
step_2 = Step('return_response', Return('request_result'))
w.add_step(step_2)

if __name__ == '__main__':
    print(w.to_yaml())