# Cloud Workflows SDK

This is unofficial SDK for [Google Cloud Workflows](https://cloud.google.com/workflows/).  
**Why to write YAML or JSON file to create a workflow when we could do it in Python?**

This package behaves like wrapper for various Workflows objects and in the end generates YAML code (no rocket science).  
It doesn't provide local simulator. 
Main idea/motivation behind this project:  
- write workflow in Python (not YAML or JSON)(nothing against YAML or JSON, for some people it isn't so convenient)   
- reuse existing steps/workflows  

SDK follows closely Workflows naming and conventions

take a look at [samples](./samples) folder to get the idea how workflows look like.
At the moment, this is just simple Proof of Concept to see if/how it could be done and to get feedback. 

## Install
via pypi
`pip install cloud-workflows`  
or from code
`python setup.py install`

## Get started with workflows
Structure of library:  
`workflows` - base objects   
`workflows.standard` - some functions from Workflows Standard library (not complete)  
`workflows.connectors` - here are some Google Cloud connectors with subset of functions. Definitely not complete list,
but can be easily extended  

## Main components
`Workflow` - (main) Workflow  
`Subworkflow`  - Subworkflow definition  
`Step` - A single step in a workflow  
`Return` - set variable as return  
`Raise` - raise exception   
`Retry` - Rules for retry  
`Backoff` - back off config for Retry

## Concepts
As examples explaining concepts and usage, I am using code snippets, not fully functional workflows. For full functional examples, take a look at 
[samples](./samples)

## Workflow

```python
w = Workflow()
```
using input parameters
```python
w = Workflow(params='[args]')
```
input parameters are enclosed in string and bracket '[args]', similar for multiple input variables 
```python
w = Workflow(params='[args1, args2]')
```
Workflow consist of steps (one or more). Every Step consists of name, "operation" and either 'result' or 'return' and you can
set 'next' step.

## Step

Step is defined with a name, "operation", and optionally next (step).  
For example, this step is called 'log_wiki_response' and it calls `SysLog` operation which is shortcut for `sys.log` 
native Workflows function
```python
Step('log_wiki_response', SysLog(json='${wikiResult}'))
```

```yaml
- log_wiki_response:
  call: sys.log
  args:
    json: ${wikiResult}
```

next Step can be defined as a string 
```python
Step('getCurrentTime', Http('get', 'https://us-central1-workflowsample.cloudfunctions.net/datetime',
                result='currentDateTime'), next_='next_step_name')
```
or pass Step instance
```python
end_step = Step('end_step', Return('output'))
Step('getCurrentTime', Http('get', 'https://us-central1-workflowsample.cloudfunctions.net/datetime',
                result='output'), next_=end_step)
```

## Operations
Step Operation can variable Assign, Call, TryExceptRetry, For (loop), Switch, Raise, Return, SubWorkflow

### Variables & Expressions
Variables are defined as strings.  
Same is with expressions ( ${some_variable} ).  
Variable is then referenced as a string.  
Take a look at Future/TODO to read some ideas.  

Example with assigning variable. `project` variable is set with `${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}`

```python
step = Step('asign_variables', Assign(variables={'bucket': 'my-gcs-bucket',
                                                 'project': '${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}'}))
```
this generates following 
```yaml
main:
  steps:
  - asign_variables:
      assign:
      - bucket: my-gcs-bucket
      - project: ${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}
```
or assigning variables as dictionary
```python
# assign variable
Step('step_name', Assign({'myvar_name': 'myvar_value', 'myvar2': 'hello'}))
```
which generates this yaml
```yaml
- step_name:
      assign:
      - myvar_name: myvar_value
      - myvar2: hello
```
or defining variable in Call step ('request_result')
```python
Step('call_example', Call('http.get', {'url': 'https://www.gcpweekly.com/'}, 'request_result'))
```
which generates this yaml:
```yaml
- http_request_example:
      call: http.get
      args:
        url: https://www.gcpweekly.com/
      result: request_result
```

### For Operation (Iteration)
Reference: [https://cloud.google.com/workflows/docs/reference/syntax/iteration](https://cloud.google.com/workflows/docs/reference/syntax/iteration)
Example 
```python
For(list_values='${api_res.body.data}',  # here is list from API response
    loop_variable='item',  # variable name in loop step
    steps=[  # steps to execute
        # prepare row, get desired data
        Step('set_row', Assign(variables=[
            {'row':
                 {'State': '${item.State}',
                  'Year': '${item.Year}',
                  'Population': '${item.Population}',
                  }
             },
        ]
        )),
        # make BigQuery request
        Step('insert_bq',
             BigQueryTableData.insertAll('${gcp_project}', '${bq_dataset}', '${bq_table}', insert_body,
                                         'bq_insert')),
        # log response
        Step('log_item', SysLog(json='${bq_insert}', severity='INFO'))
    ])))
```
`list_values` and `loop_variable` are strings, whereas in `steps` is defined list of Steps to be executed.  
code above generates following yaml
```yaml
steps:
  - extract_data:
      for:
        value: item
        in: ${api_res.body.data}
        steps:
        - set_row:
            assign:
            - row:
                State: ${item.State}
                Year: ${item.Year}
                Population: ${item.Population}
        - insert_bq:
            call: googleapis.bigquery.v2.tabledata.insertAll
            args:
              datasetId: ${bq_dataset}
              projectId: ${gcp_project}
              tableId: ${bq_table}
              body:
                rows:
                - json: ${row}
            result: bq_insert
        - log_item:
            call: sys.log
            args:
              json: ${bq_insert}
              severity: INFO
```

### Conditions / Switch
[https://cloud.google.com/workflows/docs/reference/syntax/conditions](https://cloud.google.com/workflows/docs/reference/syntax/conditions)

`Condition` and `Switch` go together
Switch is basically list of Conditions
`Condition` is string in which logical condition is expressed, for example:  
`${ocr_status.body.metadata.state!="DONE"}` or  
`${${first_result.body.SomeField < 10}`  

Condition has 'next' step, which is executed when condition is met, and as input either Step reference can be passed or its' name.  

```python
wait_step = Step('wait_step', SysSleep(2))
step_end = Step('last_step', return_='${output}')
check_status = Step('check_status', Switch([
    Condition('${ocr_status.body.metadata.state!="DONE"}', next_=wait_step),
    Condition('${ocr_status.body.metadata.state=="DONE"}', next_='last_step')
]))
```
for full example, take a look at [vision_pdf_ocr.py](./samples/vision_pdf_ocr.py) example

### TryExceptRetry
[https://cloud.google.com/workflows/docs/reference/syntax/catching-errors](https://cloud.google.com/workflows/docs/reference/syntax/catching-errors)

`TryExceptRetry` encapsulates try/except/retry structure for error handling.  
There is a list of try Steps, Steps to execute during 'except' part
```python

TryExceptRetry([create_bq_table_step,
                Step('log_response', SysLog(json='${bq_response}')),
                Step('output', Return('${bq_response}'))
                ],
               as_='e',
               except_steps=[
                   Step('known_errors', SysLog(json='${e}')),
               ])
                )
```
this generates following yaml
```yaml
- create_bq_table:
  try:
    steps:
    - create_bq_table_req:
        call: googleapis.bigquery.v2.tables.insert
        args:
          datasetId: ${bq_dataset}
          projectId: ${gcp_project}
          body:
            tableReference:
              projectId: ${gcp_project}
              datasetId: ${bq_dataset}
              tableId: ${bq_table}
            schema:
              fields:
              - name: State
                type: STRING
              - name: Year
                type: STRING
              - name: Population
                type: INTEGER
        result: bq_response
    - log_response:
        call: sys.log
        args:
          json: ${bq_response}
    - output:
        return: ${bq_response}
  except:
    as: e
    steps:
    - known_errors:
        call: sys.log
        args:
          json: ${e}
```

### Raise
[https://cloud.google.com/workflows/docs/reference/syntax/raising-errors](https://cloud.google.com/workflows/docs/reference/syntax/raising-errors)  
Raising error/exception

```python
s = Step('raise_string', Raise('my error'))
s2 = Step('raise_dict', Raise({'code': 55, 'msg': 'my error'}))
```

```yaml
main:
  steps:
  - raise_exception:
      raise: my error
  - raise_dict:
      raise:
        code: 55
        msg: my error
```

### Retry
[https://cloud.google.com/workflows/docs/reference/syntax/retrying](https://cloud.google.com/workflows/docs/reference/syntax/retrying)

Retry allows to define either policy or predicate with other configurations in TryExceptRetry block.  
For policy retry values, there is enumeration `RetryPolicy`. This can be used also as predicate

```python
w = Workflow()
req = Http('get', 'https://www.google.com')
s = Step('policy_example',
        TryExceptRetry(
            try_steps=[req],
            retry=Retry(policy=RetryPolicy.default))
         )

s2 = Step('predicate_example',
          TryExceptRetry(try_steps=[req],
                         retry=Retry(predicate=RetryPolicy.default,
                                     max_retries=10,
                                     backoff=BackOff(1, 90, 3))
                         )
          )
```
output in yaml:
```yaml
main:
  steps:
  - policy_example:
      try:
        steps:
        - call: http.get
          args:
            url: https://www.google.com
      retry: ${http.default_retry}
  - predicate_example:
      try:
        steps:
        - call: http.get
          args:
            url: https://www.google.com
      retry:
        predicate: ${http.default_retry}
        max_retries: 10
        backoff:
          initial_delay: 1
          max_delay: 90
          multiplier: 3
```

### Return
Return is a wrapper for Step to return variable value.
Simplified example
```python
Step('http_request_example',Call('http.get', {'url': 'https://www.gcpweekly.com/'}, 'request_result'))
Step('return_response', Return('request_result'))
```
In the first step is defined variable `request_result` and in the second step is returned with `Return` object

```yaml
main:
  steps:
  - http_request_example:
      call: http.get
      args:
        url: https://www.gcpweekly.com/
      result: request_result
  - return_response:
      return: ${request_result}
```

### Subworkflows
Subworkflows are defined with class Subworkflow. They are almost the same as Workflows, i.e. they consist of a name, 
list of Steps and params. Difference with Workflow class is in output rendering

```python
w = Workflow()
# define subworkflow with name and input parameter. We'll add 2 steps
sub = SubWorkflow('make_get_req', params='[url]')
# The first step is to make request based on url input parameter
sub.add_step(Step('http_get', Http('get', '${url}', result='req_out')))
# Second step is to log response
sub.add_step(Step('log_result', SysLog(json='${req_out}', severity='INFO')))
# add subworkflow to Workflow
w.add_subworkflow(sub)

# add two calls to subworkflow
w.add_step(Step('http_get1', Call(sub, {'url': 'https://www.gcpweekly.com'})))
w.add_step(Step('http_get2', Call(sub, {'url': 'https://www.the-swamp.info'})))
```
output in yaml:

```yaml
main:
  steps:
  - http_get1:
      call: make_get_req
      args:
        url: https://www.gcpweekly.com
  - http_get2:
      call: make_get_req
      args:
        url: https://www.the-swamp.info
make_get_req:
  params: [url]
  steps:
  - http_get:
      call: http.get
      args:
        url: ${url}
      result: req_out
  - log_result:
      call: sys.log
      args:
        json: ${req_out}
        severity: INFO
```

you can add existing workflow as subworkflow. You need to rename workflow's name (if it's 'main') 
see example in `api_datausa_to_bq.py`

## Connectors 
Connectors module is implementation of Workflow connectors. At the moment very few are implemented, but it should be 
quite straightforward to implement the rest.  
It all boils to return Call operation.

One thing is that in some cases input parameters in functions are expected to be passed as variable names and in other cases values.
In some cases where "path" is constructed, like in PubSub we pass variable names
```python
name = f'${{"projects/" + {project} + "/topics/" + "{topic_name}" }}'
```
here `project_name` and `topic_name` are passed as a variable names, since whole "name" is expression. For example:
```python
w.add_step(Step('assign_step', Assign({
    'ps_topic': 'mytopic',
    'gcp_project': '${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}'
})))
w.add_step(Step('create_topic', PubSub.create_topic('ps_topic', 'gcp_project', 'ps_output')))
```

on the other hand, for example in BigQuery, input variables are expected to be values, so it's common that variables are 
wrapped as expressions when calling a function

```python
Step('create_bq_table_req',
    BigQueryTables.insert('${bq_dataset}', '${gcp_project}', bq_table_reference,
                          result='bq_response'))
```
Also for now, I'm leaving up to users to correctly construct (in some cases, quite complex) input body.
See for example [bq_create_table.py](./samples/bq_create_table.py) or [xkcd.py](./samples/xkcd.py)

## Deployment

Workflow YAML code can be generated by calling Worflow method `to_yaml()` and paste content to Cloud Console :)
```python
print(w.to_yaml())  
```
or generate content into the file with method `to_yaml_file()`
```python
w.to_yaml_file('my_workflow.yaml')
```

### Building on existing blocks

Having basic Workflows constructs, allows us not to create simpler and reusable components.  
For example Http is created based on Call (see in [workflows.core.py](./workflows/core.py))
and simplify usage of previous example to this:
```python
Http('get', 'https://cloud.google.com/workflows')
```
Other example is `workflows.connectors` module. It's completely build on top of `Call`

## Future / Thoughts / TODO

## Missing features
Some functionalities/features are not implemented, namely functions like for example `sys.get_env`. In such cases, we're
left to use hard coded string:
```yaml
Assign(variables=[    
    {'gcp_project': '${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}'}
])
```
Hopefully in some of the next releases, it will be implemented. The issue is related to how yaml renders Python objects.


### Variables
My initial idea was to provide possibility of variable definition and then reference it throughout the workflow code. 
This has advantage of potentially reducing human/typo errors. 

simple case when basically variable name is passed (pseudo code)
```python
w = Workflow()
api_response = Variable('api_res')
w.add_step(Step('fetch_data', Http('get', 'https://www.gcpweekly.com/', result=api_response)))
w.add_step(Step('return_output', Return(api_response)))
```

it would get a bit trickier if variable would have complex fields.
Pseudo code
```python
w = Workflow()

#(inspired by Django, SQLAlchemy, maybe some other structure would be simpler and sufficient)
class ApiResponse(Variable):
    body = Field()
    code = Field()
    headers = Field()
    
w.add_step(Step('fetch_data', Http('get', 'https://www.gcpweekly.com/', result=ApiResponse)))
# we could now reference just 'body'
w.add_step(Step('return_output', Return(ApiResponse.body)))
```
but I'm not sure if this would be a right direction, I'm trying to find some better ways than using strings on the 
other hand I wouldn't like to make it too much complex.

### Connectors
In connections with variables, one possible simplification would be to have defined
variables as input/outputs of GCP Connectors, where those objects can be pretty complex, so that could simplify.  
I think those definitions exists (proto messages?) and could be somehow generated into Python objects, but this is a bit
distant future.  


Versions.
There can be multiple version for product, at the moment I'm handling the latest, although it would be fine if all 
versions would be supported

### Rest
Adding Tests  
Complete rest of stuff from core/standard features  
Return should return list of variables  
Enumerations (Auth, Http methods...)  
When calling subworkflows, check if args are matching expected input parameters that subworkflow expects  
Easier deployment via Workflows API  
Generally add verifications so human errors are prevented as much as possible.  
Ability to generate JSON (theoretically it should be possible)  

