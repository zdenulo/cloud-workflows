from workflows import Workflow, Assign, Step, Switch, Condition, Return



w = Workflow(steps=[
    Step('define', Assign(variables=[{'array': ["foo", "la", "r"]}])),
    Step('check_condition', Switch([Condition('${len(array) > i}', next_='iterate')])),
    Step('iterate', Assign(variables=[{'result': '${result + array[i]}'},
                                      {'i': '${i+1}'}
                                      ]
                           ), next_='check_condition'),
    Step('exit_loop', Return('result'))

])

if __name__ == '__main__':
    print(w.to_yaml())
