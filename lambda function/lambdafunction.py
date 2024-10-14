import time
import json
import random
import requests
import os

tb_url =  #The URL of your ThingsBoard instance (e.g., https://thingsboard.com).
homeDashboardId =  #The ID of the dashboard you want to assign as the home dashboard for new customers.
deviceCloneId =  #The ID of a sample device from which telemetry data will be copied.
device_profile_id = #The ID of the device profile associated with the sample device.
keys =  #A list of telemetry keys to copy from the sample device to the new device (e.g., ["battery", "temperature"]).

def lambda_Event_handler(event):
    try:
        body = event.get('body', '{}')
        parsed_body = json.loads(body)
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid JSON format'})
        }
    return event

def get_jwt_token():
    url = f"{tb_url}/api/auth/login"
    login_payload = {
        "username": os.environ['USERNAME'], 
        "password": os.environ['PASSWORD']  
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=login_payload)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        raise Exception(f"Failed to get JWT token: {response.status_code}, {response.text}")

def api_post(endpoint, data, jwt_token, query_params="", returnJson=True):
    url = f"{tb_url}/api{endpoint}{query_params}"
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": f"Bearer {jwt_token}"
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}, {response.text}")
    
    return response.json() if returnJson else response

def api_get(endpoint, jwt_token, query_params=""):
    url = f"{tb_url}/api{endpoint}{query_params}"
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": f"Bearer {jwt_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}, {response.text}")
    
    return response.json()

def create_customer(customer_details, jwt_token):
    return api_post("/customer", customer_details, jwt_token)

def create_user_with_activation(user_details, jwt_token):
    return api_post("/user", user_details, jwt_token, "?sendActivationMail=true")

def assign_dashboard_to_customer(customer_id, jwt_token):
    url = f"{tb_url}/api/customer/{customer_id}/dashboard/{dashboard_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": f"Bearer {jwt_token}"
    }

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to assign dashboard: {response.status_code}, {response.text}")

def get_timestamps():
    now_ts = int(time.time() * 1000)
    ten_days_ago_ts = now_ts - (25 * 24 * 60 * 60 * 1000)
    return now_ts, ten_days_ago_ts

def get_device_telemetry(device_id, keys, jwt_token, start_ts, end_ts):
    url = f"{tb_url}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
    params = {"keys": keys, "startTs": start_ts, "endTs": end_ts}
    headers = {"X-Authorization": f"Bearer {jwt_token}"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching telemetry: {response.status_code}, {response.text}")

def convert_telemetry_format(data):
    combined_data = {}
    for key, readings in data.items():
        for entry in readings:
            ts = entry['ts']
            value = entry['value']
            if ts not in combined_data:
                combined_data[ts] = {"ts": ts, "values": {}}
            combined_data[ts]["values"][key] = value

    return list(combined_data.values())

def getTelemetryData(deviceCloneId, jwt_token):
    now_ts, ten_days_ago_ts = get_timestamps()
    deviceTelemetry = get_device_telemetry(deviceCloneId, keys, jwt_token, ten_days_ago_ts, now_ts)
    return convert_telemetry_format(deviceTelemetry)

def createNewDevice(jwt_token, customerId):
    device_payload = {
      "name": "Test device " + customerId[-5:], # adds last 5 digits of customer id so name is unique
      "label": "Test device",
      "deviceProfileId": {"entityType": "DEVICE_PROFILE", "id": device_profile_id},
      "additionalInfo": {"gateway": False, "overwriteActivityTime": False, "description": ""},
      "customerId": {"entityType": "CUSTOMER", "id": customerId}
    }

    response = api_post("/device", device_payload, jwt_token)
    if 'id' in response:
        return response["id"]["id"]
    else:
        raise Exception(f"Failed to create device: {response}")

def send_telemetry_data(dataParsed, jwt_token, newDeviceId):
    endpoint = f"/plugins/telemetry/DEVICE/{newDeviceId}/timeseries/ANY"
    api_post(endpoint, dataParsed, jwt_token, returnJson=False)

def createCustomer(event, jwt_token):
    random_number = str(random.randint(1, 1000))
    customer_data = {
        "title": event["title"],
        "email": event["email"],
        "phone": event["phone"],
        "name": event["email"],
        "additionalInfo": {
            "homeDashboardHideToolbar": "true",
            "homeDashboardId": homeDashboardId
        }
    }

    return create_customer(customer_data, jwt_token)

def createUser(event, jwt_token, customerId):
    user_data = {
        "authority": "CUSTOMER_USER",
        "email": event["email"], 
        "firstName": event["firstName"],
        "lastName": event["lastName"],
        "name": event["email"],
        "phone": event["phone"],
        "customerId": {"entityType": "CUSTOMER", "id": customerId},
        "additionalInfo": {"homeDashboardHideToolbar": "true", "homeDashboardId": homeDashboardId}
    }

    return create_user_with_activation(user_data, jwt_token)

def get_server_attributes(deviceCloneId, jwt_token):
    return api_get(f"/plugins/telemetry/DEVICE/{deviceCloneId}/values/attributes/SERVER_SCOPE", jwt_token)

def update_server_attributes(newDeviceId, attributes_payload, jwt_token):
    api_post(f"/plugins/telemetry/DEVICE/{newDeviceId}/attributes/SERVER_SCOPE", attributes_payload, jwt_token, returnJson=False)

def convert_attributes_to_dict(attribute_list):
    return {item['key']: item['value'] for item in attribute_list}

def lambda_handler(event, context):
    event = lambda_Event_handler(event)
    jwt_token = get_jwt_token()

    try:
        customerResponse = createCustomer(event, jwt_token)
        customerId = customerResponse["id"]["id"]

        createUser(event, jwt_token, customerId)
        assign_dashboard_to_customer(customerId, jwt_token)

        newDeviceId = createNewDevice(jwt_token, customerId)
        dataParsed = getTelemetryData(deviceCloneId, jwt_token)
        send_telemetry_data(dataParsed, jwt_token, newDeviceId)

        server_attributes = get_server_attributes(deviceCloneId, jwt_token)
        parsedServerAttributes = convert_attributes_to_dict(server_attributes)
        update_server_attributes(newDeviceId, parsedServerAttributes, jwt_token)

        return {'statusCode': 200, 'body': json.dumps(customerResponse)}

    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}
