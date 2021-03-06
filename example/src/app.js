import Analytics from '@aws-amplify/analytics';
import Auth from '@aws-amplify/auth';

// The custom tag requires the Analytics function to exist on the window
window.Analytics = Analytics

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

document.getElementById('EventButton').addEventListener('click', (evt) => {
	let search_query = document.getElementById("DataInput").value

	window.dataLayer = window.dataLayer || [];
	window.dataLayer.push({
		  event: 'MyAnalyticsEventTrigger',
		  analytics_event: "search",
		  analytics_data: search_query
	});

	alert("Analytic event triggered")
});
