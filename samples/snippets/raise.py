
from workflows import Workflow, Step, Raise

w = Workflow()
s = Step('raise_string', Raise('my error'))
s2 = Step('raise_dict', Raise({'code': 55, 'msg': 'my error'}))
w.add_step(s)
w.add_step(s2)

print(w.to_yaml())