from workflows import Call


class SQLAdminBackupRuns(object):

    @classmethod
    def insert(cls, project_id, instance, body, result=None):
        """https://cloud.google.com/workflows/docs/reference/googleapis/sqladmin/v1/backupRuns/insert"""
        api = 'googleapis.sqladmin.v1.backupRuns.insert'
        args = {
            'instance': instance,
            'project': project_id,
            'body': body
        }
        return Call(api, args, result)


class SQLInstances(object):

    @classmethod
    def update(cls, project_id, instance_id, body, result=None):
        api = 'googleapis.sqladmin.v1.instances.update'
        args = {
            'instance': instance_id,
            'project': project_id,
            'body': body
        }
        return Call(api, args, result)

    @classmethod
    def get(cls, project_id, instance_id, result=None):
        api = 'googleapis.sqladmin.v1.instances.get'
        args = {
            'instance': instance_id,
            'project': project_id
        }
        return Call(api, args, result)


class SQLAdminDatabases(object):

    @classmethod
    def insert(cls):
        pass

    @classmethod
    def delete(cls):
        pass

    @classmethod
    def get(cls):
        pass

    @classmethod
    def update(cls):
        pass

    @classmethod
    def patch(cls):
        pass

    @classmethod
    def list(cls):
        pass