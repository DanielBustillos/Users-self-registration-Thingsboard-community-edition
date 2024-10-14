# ThingsBoard Public Dashboard with User Registration and Device Management

## Overview

This project enables user to create new accounts (self registration) via a public dashboard that includes a form for collecting user information. It also sets up an AWS API Gateway to securely receive user data from the form without exposing sensitive JWT tokens directly. The data is processed via an AWS Lambda function that performs the following actions:

- Creates a new customer and user in ThingsBoard.
- Assigns the public dashboard to the newly created customer.
- Creates a new device linked to the user for monitoring purposes.

By using an API Gateway, this project ensures that tenant JWT tokens are not passed explicitly through the public dashboard, enhancing security.

![Create account dashboard](./assets/createAccountScreenShoot.png)

## Project logic

- **Public Dashboard**: Displays data and includes a form for user registration.
- **API Gateway**: Receives user information submitted from the public dashboard form.
- **Lambda Function**: Handles customer and user creation, dashboard assignment, and device creation in ThingsBoard.

![Flow diagram](./assets/flow%20diagram.png)
## Prerequisites

Before setting up this project, ensure you have the following:

- **ThingsBoard on premise**: A running instance of ThingsBoard.
- **AWS Account**: To create the API Gateway and Lambda function.
- **Email smtp configure** configure smtp credential from custom mail to be able to send mails. I use Zoho mail for this purpose.
- **Sample device** create a sample device with a device profile. This device will be copied and assigned to new customer. This is necesary because Community edition does not let you to assign many customers to a single device.

## Step-by-Step Process:


### 1. Create the Lambda Function

The Lambda function is responsible for handling user registration and device setup when triggered by the API Gateway. It performs the following tasks:

- Generates a JWT token using tenant credentials.
- Creates a new customer using the information received from the form.
- Assigns a public dashboard to the newly created customer.
- Sets the public dashboard as the home dashboard for the customer.
- Creates a new device linked to the customer.
- Copies telemetry data from a sample device to the new device.
- Updates server-side attributes for the new device.

#### Steps to Create the Lambda Function:

1. **Create a new Lambda function** in the AWS Lambda console.
   - Go to the AWS Lambda console and create a new function.
   - Copy and paste the code from the `lambda function` folder of this repository into the function editor.

2. **Edit the following placeholder definitions in the Lambda function code**:
   - `tb_url`: The URL of your ThingsBoard instance (e.g., `https://thingsboard.com`).
   - `homeDashboardId`: The ID of the dashboard you want to assign as the home dashboard for new customers.
   - `deviceCloneId`: The ID of a sample device from which telemetry data will be copied.
   - `device_profile_id`: The ID of the device profile associated with the sample device.
   - `keys`: A list of telemetry keys to copy from the sample device to the new device (e.g., `["battery", "temperature"]`).

3. **Set environment variables** in the Lambda console:
   - In the Lambda function settings, under **Environment Variables**, add the following variables:
     - `USERNAME`: Your ThingsBoard tenant username.
     - `PASSWORD`: Your ThingsBoard tenant password.

4. **Test the Lambda function**:
   - In the Lambda console, open the **Test** tab and create a new test event using the following sample JSON payload:
   
   ```json
   {
     "title": "New Customer",
     "email": "your@email.com",
     "firstName": "John",
     "lastName": "Doe",
     "phone": "1234567890"
   }

 
- Add your user name and password ans env variables
- Fill 
 
### 2. Set Up API Gateway in AWS

**Objective**: Securely pass user data from the ThingsBoard dashboard to the backend without exposing sensitive information.

- In AWS, navigate to **API Gateway** and create a new REST API.
- Create a **POST** method for the endpoint (e.g., `/register`).
  - This endpoint will receive the user data from the dashboard's form.
- Set up the POST method to trigger the AWS Lambda function that processes the user registration and device setup.


### 3. Create a Public Dashboard in ThingsBoard
**Objective**: Build a public-facing dashboard that includes a user registration form.
- In ThingsBoard, create a new public dashboard. This dashboard will allow users to interact with and register their details.
- Upload html widget contained in dashboard folder.
- Configure env variables marked as #toFill
- For better styling, modify this in Dashboard settings:
  - In dashboard settings:
    - hide tool bar
    - enable "Auto fill layout height"
    - Configure background color as needed
    - Disable Apply margin to the sides of the layout


**Security Consideration**: The API Gateway will handle communication between the public dashboard and the backend. This ensures that JWT tokens are not exposed in the browser.

---


**Environment Variables**: Set the necessary environment variables for the Lambda function:

```bash
TB_URL=https://<your-thingsboard-url>
USERNAME=<your-tenant-username>
PASSWORD=<your-tenant-password>
DASHBOARD_ID=<your-dashboard-id>
DEVICE_PROFILE_ID=<your-device-profile-id>
HOME_DASHBOARD_ID=<your-home-dashboard-id>
