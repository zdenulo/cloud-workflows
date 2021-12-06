"""
Well know example of Wiki which we see everytime we want to create a Workflow in Cloud Console
"""
from workflows import Workflow, Step, Switch, Condition, Assign, Http, Return
from workflows.standard import SysLog

w = Workflow(params=["input"])

# step with the Switch and Conditions.
# In condition we are adding step which assign variable
check_input = Step('checkSearchTermInInput', Switch([
    Condition('${"searchTerm" in input}', steps=[Step('assign_vars', Assign({'searchTerm': '${input.searchTerm}'}))],
              next_='readWikipedia')
]))

w.add_step(check_input)

# make HTTP request
w.add_step(Step('getCurrentTime', Http('get', 'https://us-central1-workflowsample.cloudfunctions.net/datetime',
                result='currentDateTime')))

# log response
w.add_step(Step('log_current_time_response', SysLog(json='${currentDateTime}')))
# assign response to variable
w.add_step(Step('setFromCallResult', Assign({'searchTerm': '${currentDateTime.body.dayOfTheWeek}'})))

# make HTTP request with parameters
w.add_step(Step('readWikipedia', Http('get', 'https://en.wikipedia.org/w/api.php',
                                      query={'action': 'opensearch',
                                             'search': '${searchTerm}'
                                             }, result='wikiResult')))
# log response
w.add_step(Step('log_wiki_response', SysLog(json='${wikiResult}')))
w.add_step(Step('returnOutput', Return('${wikiResult.body[1]}')))

if __name__ == '__main__':
    print(w.to_yaml())
