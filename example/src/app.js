import Analytics from '@aws-amplify/analytics';
import Auth from '@aws-amplify/auth';

//--- Enter your Cognito and Pinpoint configuration below: ---

Auth.configure({
	Auth: {
		identityPoolId: 'your-identity-pool-id',
		region: 'your-region'
	}
})

Analytics.configure({
	AWSPinpoint: {
		appId: 'your-pinpoint-app-id',
		region: 'your-region',
		mandatorySignIn: false,
	}
})

//------------------------------------------------------------

document.getElementById('MutationEventButton').addEventListener('click', (evt) => {

	const resultElement = document.getElementById('MutationResult')

	resultElement.innerHTML = `Recording event... `;

	window.dataLayer = window.dataLayer || [];
	window.dataLayer.push({
	  event: 'AmplifyAnalyticsEvent',
	  data: {
		  'field1': 123,
		  'field2': 'hello world'
	  }
	});
});

window.amplify_tag_callback = event => {
	console.log("Sending event to Amplify Analytics:", event)

	Analytics.record(event.data).then(r => {
		resultElement.innerHTML += "Success"
	})
	.catch(e => {
		console.log("Error:", e)
		resultElement.innerHTML += "An error occurred"
	})
}
