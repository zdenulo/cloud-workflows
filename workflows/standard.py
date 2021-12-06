"""
Implementation of the functionalities from a standard library
"""
from workflows.core import BaseObject, Call


# TODO add enumeration for Log Severity

class SysLog(Call):
    """Representation of sys.log"""

    def __init__(self, data: str = None, text: str = None, json: str = None, severity='DEFAULT'):
        args = dict()
        if data:
            args['data'] = data
        elif text:
            args['text'] = text
        elif json:
            args['json'] = json
        if severity != 'DEFAULT':
            args['severity'] = severity
        super(SysLog, self).__init__('sys.log', args)


class SysSleep(Call):
    """Representation of sys.sleep"""

    def __init__(self, seconds):
        if seconds > 31536000:
            raise Exception('Over limit')
        super(SysSleep, self).__init__('sys.sleep', {'seconds': seconds})
