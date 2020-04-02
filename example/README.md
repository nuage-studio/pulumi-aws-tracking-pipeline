# Amplify Analytics Example

This project contains a simple JavaScript website using the Amplify library which sends test events to an AWS Pinpoint application, such as the one created by the `nuage:aws:Analytics` component.

To run this example you will need node.js version 12 or higher.  You will also need the AWS CLI (with correctly configured credentials) and the [Amplify CLI](https://aws-amplify.github.io/docs/).

To launch the website:

* Run the Pulumi program in the root of this project, such that it presents a list of outputs.
* Update the configuration in `app.js` to use your Pinpoint appliction and the Identity Pool created in the last step.
* Copy the GTM tags from the outputs into the appropriate places in `index.html` (note: to avoid special characters being escaped, try `pulumi stack` to get outputs)
* Run `npm install`
* Run `npm start` and visit `localhost:8080` in your web browser.  Enter a search query and click search.  This will trigger the tag, logging the event in Amplify.  Note that events will take a minute or so to appear in Pinpoint, and will take 5 minutes to appear in S3.

Note the following code which actually triggers the event:

```javascript
	window.dataLayer = window.dataLayer || [];
	window.dataLayer.push({
		  event: 'MyAnalyticsEventTrigger',
		  search_field: search_data
	});
```

Both the event name and the `search_field` key are dependent upon the Pulumi
configuration.  The former must be set to the `event_name` output, while the latter
can be configured using the `gtm_variables` parameter which is passed to the
`Analytics` constructor.  Any number of variables can be added.
