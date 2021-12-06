from workflows import Call


class Firestore(object):

    @classmethod
    def exportDocuments(cls, project_id, collection_ids, outputUriPrefix, database_id='(default)', result=None):
        api = 'googleapis.firestore.v1.projects.databases.exportDocuments'
        if database_id == '(default)':
            name = f'${{"projects/" + {project_id} + "/databases/" + "{database_id}" }}'
        else:
            name = f'${{"projects/" + {project_id} + "/databases/" + {database_id} }}'
        args = {
            'name': name,
            'body': {
                'collectionIds': collection_ids,
                'outputUriPrefix': outputUriPrefix
            }
        }
        return Call(api, args=args, result=result)

    @classmethod
    def importDocuments(cls, project_id, collection_ids, inputUriPrefix, database_id='(default)', result=None):
        api = 'googleapis.firestore.v1.projects.databases.importDocuments'
        name = f'${{"projects/" + {project_id} + "/databases/" + "{database_id}" }}'
        args = {
            'name': name,
            'body': {
                'collectionIds': collection_ids,
                'inputUriPrefix': inputUriPrefix
            }
        }
        return Call(api, args=args, result=result)


class FirestoreDocuments(object):

    @classmethod
    def createDocument(cls, project_id, collection_id, body, database_id='(default)', document_id=None, result=None):
        api = 'googleapis.firestore.v1.projects.databases.documents.createDocument'
        parent = f'${{"projects/" + {project_id} + "/databases/" + "{database_id}" + "/documents"  }}'
        args = {
            'collectionId': collection_id,
            'parent': parent,
            'body': body
        }
        if document_id:
            args['documentId'] = document_id
        return Call(api, args=args, result=result)