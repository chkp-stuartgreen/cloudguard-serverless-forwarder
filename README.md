# CloudGuard Serverless forwarder

This is a helper function that will allow you to forward events from CloudGuard CNAPP to a destination of your choice with additional headers for authentication.


# Instructions for use
- It should be deployed as an Azure Function App - but could be modified to run in AWS Lambda (probably). When it's deployed - make a note of your function URL.
- Go to configuration properties of your function and set an environment variable named private_auth_token. This can be whatever value you like but serves to provide mutual authentication between CloudGuard and your function. Make a note of it - you'll need it in the CloudGuard configuration.
- On the CloudGuard side - set up a new notification of type HTTP endpoint. Add in the URL of your function app here and click test, verify it succeeds and click save. Make a note of the name.
- Create a remediation action for the rule
- Create a continuous posture policy binding the ruleset, rule or entity to trigger on, and the notification you create earlier. Under 'Add Cloudbot' choose 'custom' and format your string as follows.

```
cloudbot {"client_token":"35fd6d00-45b1-4686-81ea-45cc69717576","payload":"","destination":"https://webhook.site/blah","method":"POST","headers":{"x-test-header":"custom-header"}}
```
Values:
cloudbot - name can be anything, but make sure there's a single space between this value and the following JSON
client_token: This should match what was defined as your environment variable on the function.
payload: Not currently used, can be a blank string but must be present.
destination: this should be where the event is forwarded to.
method: GET / POST. 
headers: (Object). Will be added for the onward request. In the example above - we add a header named x-test-header with a value of customer-header. This parameter can be absent if no additional headers are required.

The last two steps should be repeated for any other rules you wish to forward with additional headers. If you are looking to simple forward all events for a given ruleset - the script could be modified to ignore the destination provided by the cloudbot auto remediation parameter on the CloudGuard side and simply forward to a fixed destination. If you need info on this, let me know :).
