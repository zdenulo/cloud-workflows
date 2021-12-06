from workflows import Call


class BigQuery(object):
    @classmethod
    def list_datasets(cls, project_id, result=None):
        api = 'googleapis.bigquery.v2.datasets.list'
        return Call(api, {'projectId': project_id}, result)


class BigQueryJobs(object):
    @classmethod
    def insert(cls, projectId, body, result=None):
        api = 'googleapis.bigquery.v2.jobs.insert'
        args = {
            'projectId': projectId,
            'body': body
        }
        return Call(api, args, result)

    @classmethod
    def query(cls, project_id, body, result=None):
        api = 'googleapis.bigquery.v2.jobs.query'
        args = {'projectId': project_id, 'body': body}
        return Call(api, args, result)

    @classmethod
    def get(cls, job_id, project_id, location, result=None):
        api = 'googleapis.bigquery.v2.jobs.get'
        args = {
            'jobId': job_id,
            'projectId': project_id,
            'location': location
        }
        return Call(api, args, result)

    @classmethod
    def getQueryResults(cls, job_id, project_id, location, result=None):
        api = 'googleapis.bigquery.v2.jobs.getQueryResults'
        args = {
            'jobId': job_id,
            'projectId': project_id,
            'location': location
        }
        return Call(api, args, result)


class BigQueryTableData(object):

    @classmethod
    def insertAll(cls, project_id, dataset_id, table_id, body, result=None):
        api = 'googleapis.bigquery.v2.tabledata.insertAll'
        args = {
            'datasetId': dataset_id,
            'projectId': project_id,
            'tableId': table_id,
            'body': body
        }
        return Call(api, args, result)


class BigQueryTables(object):

    @classmethod
    def insert(cls, dataset_id, project_id, body, result=None):
        """
        https://cloud.google.com/workflows/docs/reference/googleapis/bigquery/v2/tables/insert
        :param dataset_id:
        :param project_id:
        :param body:
        :param result:
        :return:
        """
        api = 'googleapis.bigquery.v2.tables.insert'
        args = {
            'datasetId': dataset_id,
            'projectId': project_id,
            'body': body
        }
        return Call(api, args, result)

