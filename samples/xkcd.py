"""
Getting data from XKCD API (daily) and insert one row into Firestore
"""

from workflows import Workflow, Step, Http, Assign, Return
from workflows.standard import SysLog
from workflows.connectors.firestore import FirestoreDocuments

w = Workflow()

# fetch data from API
w.add_step(Step('fetch_data', Http('get', 'https://xkcd.com/info.0.json', result='api_res')))
w.add_step(Step('log_response', SysLog('${api_res}')))
# extract necessary fields into format which Firestore expects
w.add_step(Step('set_document', Assign(variables=[
    {'gcp_project': '${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}'},
    {
        'doc': {
            'fields': {
                'month': {
                    'stringValue': '${api_res.body.month}'
                },
                'num': {
                    'integerValue': '${api_res.body.num}'
                },
                'link': {
                    'stringValue': '${api_res.body.link}'
                },
                'year': {
                    'stringValue': '${api_res.body.year}'
                },
                'news': {
                    'stringValue': '${api_res.body.news}'
                },
                'safe_title': {
                    'stringValue': '${api_res.body.safe_title}'
                },
                'transcript': {
                    'stringValue': '${api_res.body.transcript}'
                },
                'alt': {
                    'stringValue': '${api_res.body.alt}'
                },
                'img': {
                    'stringValue': '${api_res.body.img}'
                },
                'title': {
                    'stringValue': '${api_res.body.title}'
                },
                'day': {
                    'stringValue': '${api_res.body.day}'
                }
            }
        }
    }])
                )
           )

# insert row/create Document into Firestore
w.add_step(Step('insert_data', FirestoreDocuments.createDocument('gcp_project', 'xkcd', '${doc}', result='fs_res')))
w.add_step(Step('out', Return('fs_res')))

if __name__ == '__main__':
    print(w.to_yaml())
