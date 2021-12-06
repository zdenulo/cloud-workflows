from workflows import Call, Http


class Vision(object):

    @classmethod
    def asyncBatchAnnotate(cls, body, result=None):
        url = 'https://vision.googleapis.com/v1/files:asyncBatchAnnotate'
        headers = {
            'Content-Type': 'application/json'
        }
        auth = 'OAuth2'
        return Http('post', url, body=body, headers=headers, auth=auth, result=result)

    @classmethod
    def getJob(cls, job_id, result=None):
        auth = 'OAuth2'
        url = f'${{"https://vision.googleapis.com/v1/" + {job_id}}}'
        return Http('get', url, auth=auth, result=result)
