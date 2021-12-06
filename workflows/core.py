import enum
from typing import Union, List

import yaml

yaml.emitter.Emitter.prepare_tag = lambda self, tag: ''
yaml.Dumper.ignore_aliases = lambda *args: True  # avoid references in yaml
from yamlable import yaml_info, YamlAble

YAML_INDENT = 4


class BaseObject(YamlAble):
    """Base object for yaml conversion"""
    __yaml_tag_suffix__ = ''

    def to_dict(self):
        raise NotImplemented

    def to_yaml(self):
        yaml_content = yaml.dump(self.to_dict(), indent=YAML_INDENT, sort_keys=False)
        return yaml_content

    def __repr__(self):
        # return json.dumps(self.to_dict())
        dict_val = str(self.to_dict())
        return dict_val

    def __to_yaml_dict__(self):
        dict_repr = self.to_dict()
        return dict_repr


class Workflow(BaseObject):

    def add_step(self, step):
        if not isinstance(step, Step):
            raise Exception("You need to add Step")
        for s in self.steps:
            if s.name == step.name:
                raise Exception(f"Step with {step.name} already exists")
        self.steps.append(step)

    def add_subworkflow(self, sub_workflow: Union['Workflow', 'SubWorkflow']):
        if isinstance(sub_workflow, Workflow):
            sub_workflow = SubWorkflow(sub_workflow.name, sub_workflow.steps, sub_workflow.params)
        for subw in self.subworkflows:
            if sub_workflow.name == subw.name:
                raise Exception("Subworkflow with name {sub_workflow.name} already exists")
        if self.name == sub_workflow.name:
            raise Exception("Subworkflow cannot have the same name as the main workflow")
        self.subworkflows.append(sub_workflow)

    def __init__(self, name='main', steps=None, params=None):
        self.params = params
        self.name = name
        if steps:
            self.steps = steps
        else:
            self.steps = []
        self.subworkflows = []

    def to_dict(self):
        workflow = dict()
        if self.params:
            workflow['params'] = str(self.params)
        workflow['steps'] = self.steps

        out = {self.name: workflow}
        for subworkflow in self.subworkflows:
            out[subworkflow.name] = subworkflow
        return out

    def to_yaml_file(self, filepath):
        with open(filepath, 'w') as f:
            f.write(self.to_yaml())

    def to_yaml(self):
        yaml_content = yaml.dump(self.to_dict(), indent=2, sort_keys=False)
        lines = []
        for line in yaml_content.split('\n'):
            if 'params' in line:
                line = line.replace("'", '')
                lines.append(line)
            else:
                lines.append(line)
        return "\n".join(lines)


class SubWorkflow(Workflow):
    """Wrapper for Sub workflows"""

    def to_dict(self):
        workflow = dict()
        if self.params:
            workflow['params'] = str(self.params)
        workflow['steps'] = self.steps

        return workflow


class Operation(BaseObject):
    pass


class Step(BaseObject):
    """Step representation"""

    def __init__(self, name: str, operation: Operation, next_=None):
        self.name = name
        self.operation = operation
        self.next_ = next_

    def to_dict(self):
        operation = self.operation.to_dict()

        if self.next_:
            if isinstance(self.next_, Step):
                operation['next'] = self.next_.name
            else:
                operation['next'] = self.next_
        out = {self.name: operation}
        return out


# TODO add possibility or return list of variables
class Return(Operation):
    """Wrapper to return variable in a Step

    usage:
    Return('my_var_name') or
    Return('${my_var_name}')
    """

    def __init__(self, return_: str):
        """
        :param return_: Name of the variable to return
        """
        if not return_:
            raise Exception('Variable name cannot be empty')
        self.return_ = return_

    def to_dict(self):
        if self.return_[0] == '$':
            out = {'return': self.return_}
        else:
            out = {'return': f'${{{self.return_}}}'}
        return out


class Raise(Operation):
    """Raise error/exception
    https://cloud.google.com/workflows/docs/reference/syntax/raising-errors

    s = Step('raise_string', Raise('my error'))
    s2 = Step('raise_dict', Raise({'code': 55, 'msg': 'my error'}))
    """

    def __init__(self, raise_: Union[str, dict] = None):
        self.raise_ = raise_

    def to_dict(self):
        return {'raise': self.raise_}


class BackOff(BaseObject):
    """Back off object which used in Retry
    https://cloud.google.com/workflows/docs/reference/syntax/retrying
    """

    def __init__(self, initial_delay: int, max_delay: int, multiplier: int):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.multiplier = multiplier

    def to_dict(self):
        out = {
            'initial_delay': self.initial_delay,
            'max_delay': self.max_delay,
            'multiplier': self.multiplier
        }
        return out


# this doesn't work in yaml
class RetryPolicy(enum.Enum):
    """Enumeration for Default Retry policy values"""

    default = '${http.default_retry}'
    default_non_idempotent = '${http.default_retry_non_idempotent}'


class Retry(Operation):
    """Custom Retry definition

    https://cloud.google.com/workflows/docs/reference/syntax/retrying
    """

    def __init__(self, policy: Union[str, RetryPolicy] = None, predicate: Union[str, RetryPolicy] = None,
                 max_retries: int = None, backoff: BackOff = None):
        if policy and (predicate or max_retries or backoff):
            raise Exception("If policy variable is set, other variables shouldn't be")

        if policy and isinstance(policy, RetryPolicy):
            self.policy = policy.value
        else:
            self.policy = policy
        if predicate and isinstance(predicate, RetryPolicy):
            self.predicate = predicate.value
        else:
            self.predicate = predicate
        self.max_retries = max_retries
        self.backoff = backoff

    def to_dict(self):
        out = dict()
        if self.policy:
            out['policy'] = self.policy_
        else:
            if self.predicate:
                out['predicate'] = self.predicate
            if self.max_retries:
                out['max_retries'] = self.max_retries
            if self.backoff:
                out['backoff'] = self.backoff
        return out


class TryExceptRetry(Operation):
    """https://cloud.google.com/workflows/docs/reference/syntax/catching-errors
    Implementation of try/except/retry structure for error handling
    """

    def __init__(self, try_steps: List[Step], retry: Retry = None, as_: str = None, except_steps: List[Step] = None):
        self.try_steps = try_steps
        self.retry = retry
        self.as_ = as_
        self.except_steps = except_steps

    def to_dict(self):
        out = dict()
        out['try'] = {'steps': self.try_steps}

        if self.retry:
            if self.retry.policy:
                out['retry'] = self.retry.policy
            else:
                out['retry'] = self.retry
        if self.except_steps:
            except_block = dict()
            if self.as_:
                except_block['as'] = self.as_
            except_block['steps'] = self.except_steps
            out['except'] = except_block

        return out


class Call(Operation):

    def __init__(self, call: Union[str, SubWorkflow], args=None, result=None):
        self.call = call
        self.args = args
        self.result = result

    def to_dict(self):
        out = dict()
        if isinstance(self.call, SubWorkflow):
            out['call'] = self.call.name
        else:
            out['call'] = self.call
        if self.args:
            out['args'] = self.args
        if self.result:
            out['result'] = self.result
        return out


class Condition(BaseObject):
    def __init__(self, condition: str, next_: Union[str, Step] = None, steps: List[Step] = None):
        """

        :param condition: string representation of evaluating condition
        :param next_: next step, if condition is true
        :param steps: list of Steps to execute
        """
        self.condition = condition
        self.next_ = next_
        self.steps = steps

    def to_dict(self):
        out = {'condition': self.condition}
        if self.steps:
            out['steps'] = self.steps
        if self.next_:
            if isinstance(self.next_, Step):
                out['next'] = self.next_.name
            else:
                out['next'] = self.next_
        return out


class Switch(Operation):
    def __init__(self, conditions: List[Condition], next_: Union[str, Operation] = None):
        self.conditions = conditions
        self.next_ = next_

    def to_dict(self):
        conditions = []
        for condition in self.conditions:
            conditions.append(condition)
        out = {'switch': conditions}
        if self.next_:
            out['next'] = self.next_
        return out


class For(Operation):
    """https://cloud.google.com/workflows/docs/reference/syntax/iteration
    """

    def __init__(self, list_values: str, loop_variable: str, steps: list, index_variable: str = None, range_=None):
        self.value = loop_variable
        self.index = index_variable
        self.in_ = list_values
        self.steps = steps
        self.range_ = range_

    def to_dict(self):
        for_dict = {'value': self.value, 'in': self.in_, 'steps': self.steps}
        if self.index:
            for_dict['index'] = self.index
        if self.range_:
            for_dict['range'] = self.range_

        out = {'for': for_dict}
        return out


class Assign(Operation):
    """Represents assigning variables
    Example of usage:

    allowed formats:
    list of dictionaries:
    Assign([{
    dictionary with multiple keys
    """

    def __init__(self, variables: Union[List[dict], dict]):
        self.variables = variables

    def to_dict(self):
        if isinstance(self.variables, dict):
            var_dict = []
            for k, v in self.variables.items():
                var_dict.append({k: v})
            variables = var_dict
        elif isinstance(self.variables, list):
            variables = self.variables
        else:
            raise Exception("only list or dictionary allowed")
        out = {'assign': variables}
        return out


class Http(Call):
    """Shortcut to make HTTP Calls, exposing usual fields"""
    _allowed_methods = ('get', 'post', 'patch', 'head', 'delete')

    def __init__(self, method: str, url: str, headers: dict = None, query: dict = None, body: dict = None,
                 auth: str = None, timeout=None, result=None):

        method_lower = method.lower()
        if method_lower not in self._allowed_methods:
            raise Exception(f'Not expected {method} as http method. Possible values are {self._allowed_methods}')
        call = f'http.{method_lower}'
        args = dict()
        args['url'] = url
        if headers:
            args['headers'] = headers
        if query:
            args['query'] = query
        if body:
            args['body'] = body
        if auth:
            args['auth'] = {'type': auth}
        if timeout:
            args['timeout'] = timeout
        super(Http, self).__init__(call, args, result)
