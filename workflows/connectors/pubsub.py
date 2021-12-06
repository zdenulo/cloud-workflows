from workflows import Call
from workflows.standard import Base64Encode


class PubSub(object):
    @classmethod
    def create_topic(cls, topic_name, project, result=None):
        api = 'googleapis.pubsub.v1.projects.topics.create'
        name = f'${{"projects/" + {project} + "/topics/" + {topic_name} }}'
        return Call(api, {'name': name}, result=result)

    @classmethod
    def publish_message(cls, topic_name, project_name, message, encode=False, result=None):
        api = 'googleapis.pubsub.v1.projects.topics.publish'
        topic_path = f'${{"projects/" + {project_name} + "/topics/" + {topic_name} }}'
        if encode:
            body = {'messages': [{'data':  '${base64.encode(message)}'}]}
        else:
            body = {'messages': [{'data': f'${{{message}}}'}]}
        args = {
            'topic': topic_path,
            'body': body
        }
        return Call(api, args, result=result)

