from workflows import Call


class SecretManager(object):

    def getSecret(self, name, result=None):
        api = 'googleapis.secretmanager.v1.projects.secrets.get'
        args = {
            'name': name
        }
        return Call(api, args, result=result)

    def accessString(self, secret_id, project_id, version=None, result=None):
        api = 'googleapis.secretmanager.v1.projects.secrets.versions.accessString'
        args = {
            'secret_id': secret_id,
            'project_id': project_id
        }
        if version:
            args['version'] = version
        return Call(api, args, result)
