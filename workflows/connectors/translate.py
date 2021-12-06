from workflows import Call


class Translate(object):

    @classmethod
    def translate(cls, query, from_language, to_language, format="text", result=None):
        api = 'googleapis.translate.v2.translations.translate'
        args = {
            'q': query,
            'target': to_language,
            'source': from_language,
            'format': format
        }
        return Call(api, args, result)


class TranslateProjects(object):
    @classmethod
    def translateText(cls, project_id, body, location='global', result=None):
        api = 'googleapis.translate.v3.projects.translateText'
        parent = f'${{"projects/" + {project_id} + "/locations/" + {location} }}'
        args = {
            'parent': parent,
            'body': body
        }
        return Call(api, args, result)