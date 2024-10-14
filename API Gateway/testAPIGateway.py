import requests
import json

# Define the API endpoint
api_url = your-api-endpoint e.g. https://XXXXXXX.execute-api.XXXX.amazonaws.com/[apiName]/[endpoinName]"

# Define headers (include API key if required)
headers = {
    "Content-Type": "application/json",
    "x-api-key": your-API-token
}

data = {
    "title": "New Custromer",
    "email": "your@email.com",
    "firstName": "John",
    "lastName": "Doe", 
    "phone": "your number"}


# Make the POST request
try:
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    
    # Check the response status
    if response.status_code in [200, 201]:
        print("Response Data:", response.json())
    else:
        print(f"Request failed with status code {response.status_code}")
        print("Response:", response.text)
        
except requests.exceptions.RequestException as e:
    print("An error occurred:", e)
