"""Example of using Retry and BackOff policy in Try/Except"""

from workflows import Step, Retry, BackOff, Workflow, TryExceptRetry, Http, RetryPolicy

w = Workflow()
req = Http('get', 'https://www.google.com')
s = Step('policy_example',
        TryExceptRetry(
            try_steps=[req],
            retry=Retry(policy=RetryPolicy.default))
         )
w.add_step(s)

s2 = Step('predicate_example',
          TryExceptRetry(try_steps=[req],
                         retry=Retry(predicate=RetryPolicy.default,
                                     max_retries=10,
                                     backoff=BackOff(1, 90, 3))
                         )
          )
w.add_step(s2)

if __name__ == '__main__':
    print(w.to_yaml())