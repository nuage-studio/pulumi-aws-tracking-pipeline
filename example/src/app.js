import Analytics from '@aws-amplify/analytics';
import Auth from '@aws-amplify/auth';

// Enter your Cognito and Pinpoint configuration below:

Auth.configure({
	Auth: {
		identityPoolId: 'your-identity-pool',
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

///

document.getElementById('MutationEventButton').addEventListener('click', (evt) => {

	const resultElement = document.getElementById('MutationResult')

	resultElement.innerHTML = `Recording event... `;

	Analytics.record({
		name: 'NuageTest',
		attributes: { field1: 'The button was clicked', field2: 'Value2' }
	}).then(r => {
		resultElement.innerHTML += "Success"
	})
	.catch(e => {
		resultElement.innerHTML += "An error occurred"
		console.log("ERROR", e)
	})
});
