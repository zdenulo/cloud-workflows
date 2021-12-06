
from workflows import Workflow, Step, Assign

w = Workflow()

w.add_step(Step('step_name', Assign({'myvar_name': 'myvar_value', 'myvar2': 'hello'})))

if __name__ == '__main__':
    print(w.to_yaml())