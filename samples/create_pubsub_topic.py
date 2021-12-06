from workflows import Workflow, Step, Return, Assign
from workflows.connectors.pubsub import PubSub

w = Workflow()
w.add_step(Step('assign_step', Assign({
    'topic': 'mytopic',
    'gcp_project': '${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}'
})))

w.add_step(Step('create_topic', PubSub.create_topic('topic', 'gcp_project', 'ps_output')))
w.add_step(Step('return', Return('ps_output')))

if __name__ == '__main__':
    print(w.to_yaml())
