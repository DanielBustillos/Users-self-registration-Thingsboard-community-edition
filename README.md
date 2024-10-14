# ThingsBoard Public Dashboard with User Registration and Device Management

This project enables user self-registration via a customizable public dashboard in ThingsBoard Community Edition. It integrates AWS API Gateway and a Lambda function to securely and cost-effectively collect user data without exposing sensitive JWT tokens, while interacting with ThingsBoard's API methods. The AWS Lambda function processes the following tasks:

- Creates a new customer and user in ThingsBoard.
- Assigns a custom dashboard to the newly created customer and sets it as the home dashboard.
- Creates a new device linked to the user.

By leveraging AWS API Gateway and Lambda, this project offers a secure and affordable solution, ensuring tenant JWT tokens are not exposed on the public dashboard while keeping operational costs low.

![Create account dashboard](./assets/createAccountScreenShoot.png)


> **Note**: The `createUser` ThingsBoard endpoint requires a JWT token from the tenant. While it is technically possible to pass the JWT directly from the dashboard without using AWS Lambda and API Gateway, this approach is highly insecure. If the JWT token is exposed in the frontend, it can easily be stolen and misused. To mitigate this risk, the tenant JWT token is securely enclosed within the AWS Lambda function, ensuring it is never exposed to the public.


> **Note**: The current code includes some workarounds designed to function safely. For example, a new device is created for each new account. These shortcuts are practical for enabling the auto-registration process in the ThingsBoard Community Edition. However, if you need a more efficient and scalable solution, consider upgrading to the paid version of ThingsBoard, which offers advanced features and better scalability.


## Project Logic

- **Public Dashboard**: Displays data and provides a form for user registration.
- **API Gateway**: Receives user data submitted from the dashboard form.
- **Lambda Function**: Manages user creation, dashboard assignment, and device creation in ThingsBoard.

![Flow diagram](./assets/flow%20diagram.png)

## Prerequisites

Before setting up this project, ensure you have:

- **ThingsBoard on-premise**: A running instance of ThingsBoard.
- **AWS Account**: To create the API Gateway and Lambda function.
- **Email SMTP configuration**: Set up SMTP credentials for sending emails (e.g., Zoho Mail). This is used to send confirmation to customer email address.
- **Sample Device**: Create a sample device with a device profile. This sample device will be copied and assigned to the new customer since ThingsBoard Community Edition does not allow multiple customers to share a device.

## Step-by-Step Process:

### 1. Create the Lambda Function

The Lambda function is responsible for handling user registration and device setup when triggered by the API Gateway. It performs the following tasks:

- Generates a JWT token using tenant credentials.
- Creates a new customer with the data submitted through the registration form.
- Assigns a public dashboard to the newly created customer.
- Sets the assigned dashboard as the home dashboard for the customer.
- Optionally, it can:
  - Create a new device linked to the customer (this line can be commented out in the `lambda_handler` function).
  - Copy telemetry data from a sample device to the newly created device (this line can be commented out if not needed).
  - Update server-side attributes for the new device (this line can also be commented out if not required).

#### Steps to Create the Lambda Function:

1. **Create a new Lambda function** in the AWS Lambda console.
- Go to the **AWS Lambda console** and create a new function with the following settings:
  - **Runtime**: Select **Python 3.11**.
  - **Other settings**: You can leave the remaining parameters at their default values (e.g., basic execution role, memory, timeout).

- **Copy and paste the code** from the `lambdafunction.py` folder of this repository into the Lambda function code editor.

- The Python code uses the **`requests`** library to communicate with the ThingsBoard API. AWS Lambda does not include this library by default, so you'll need to add it via a **Lambda layer**. There are two options to accomplish this:

  1. **Use a pre-built Lambda layer**:
     - Upload the provided `Lambda-layer.zip` file (found in lambda folder) as a new Lambda layer.
     - Attach the layer to your Lambda function. If necessary, you can link the layer to the function using its **Layer ARN**.

  2. **Create your own Lambda layer** (optional):
     - If you prefer, you can create a custom Lambda layer by packaging the `requests` library yourself. However, this process can be more complex and time-consuming. Using the provided `Lambda-layer.zip` is simpler and quicker.

2. **Edit the following placeholder definitions in the Lambda function code**:
   - `tb_url`: The URL of your ThingsBoard instance (e.g., `https://thingsboard.com`).
   - `homeDashboardId`: The ID of the dashboard you want to assign as the home dashboard for new customers.
   - `deviceCloneId`: The ID of a sample device from which telemetry data will be copied.
   - `device_profile_id`: The ID of the device profile associated with the sample device.
   - `keys`: A list of telemetry keys to copy from the sample device to the new device (e.g., `["battery", "temperature"]`).
  
   - **Improvement suggestion**: Define this variables as env variables.

3. **Set environment variables** in the Lambda console:
   - In the Lambda function settings, under **Environment Variables**, add the following variables:
     - `USERNAME`: Your ThingsBoard tenant username.
     - `PASSWORD`: Your ThingsBoard tenant password.
 > **Note**: While storing sensitive information like usernames and passwords in Lambda environment variables is generally considered safe (as they are encrypted and contained within the Lambda function), you can enhance security by reducing the exposure of these credentials:

   - **Improvement suggestion**: Instead of storing the username and password, consider manually generating a **JWT token** with an extended expiration time (e.g., several weeks or months). You can configure ThingsBoard to refresh this token periodically in the panel, thereby reducing the need to frequently regenerate the token.
   

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
 
### 2. Set Up API Gateway in AWS

In this step, you'll securely pass user data from the ThingsBoard dashboard to the backend without exposing sensitive information. If you're not an expert in AWS API Gateway, this is a general approach to follow. For more detailed instructions, refer to the [AWS guide](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html) or use tools like ChatGPT to help you configure it step-by-step.

#### Steps to Set Up API Gateway:

1. **Create a New REST API**:
   - In the AWS Management Console, navigate to **API Gateway** and select **Create API**.
   - Choose **REST API** and give your API a name (e.g., "User Registration API").
   - For the **Endpoint Type**, choose **Regional**.

2. **Create a POST Method**:
   - In the API Gateway dashboard, create a **POST** method under the resource path where you want to receive the user data (e.g., `/register`).
   - Select **POST** from the list of available methods.
   - For **Integration Type**, choose **Lambda Function**. Then, select the Lambda function you created in the previous step to handle user registration and device creation.

3. **Set Up Usage Plan and API Key**:
   To prevent abuse or malicious attempts to create unintended accounts, you can limit the number of API calls using a usage plan and API keys:
   
   - Create a **Usage Plan** in the API Gateway console, setting limits on the number of API calls (e.g., X requests per minute).
   - Enable **API Key Required** on the **POST** method under the resource.
   - Generate an **API Key**, which will be required for calling the API. This key should be configured and stored securely in the next steps.
   - Link the generated API Key to the usage plan you created, so that only a limited number of requests can be made with that key.

4. **Enable CORS**:
   - In the **POST** method settings, enable **CORS (Cross-Origin Resource Sharing)** to allow the ThingsBoard dashboard to communicate with your API.
   - In the CORS settings, make sure to include the URL of your ThingsBoard dashboard in the list of allowed origins.
   - Save your changes and deploy the API.
     
5. **Test API and Lambda Integration**:
   - Run `testAPIGateway.py` after updating the placeholder parameters (e.g., API URL, API key, user details).
   - Upon execution, the script should trigger the Lambda function and successfully create new users in ThingsBoard.


### 3. Create a Public Dashboard in ThingsBoard

**Objective**: Build a public-facing dashboard with a user registration form that sends data to API Gateway.

- Create a new dashboard in ThingsBoard and set it to public.
- Upload the HTML widget from the `dashboard` folder.
- Configure the following in the widget:
  - `const apiUrl = "your API URL with endpoint";`
  - `"x-api-key": "your API token";`
  - Optionally, update the logo in the `logo div` and edit css colors and styling.

- For improved styling, modify the following in Dashboard settings:
  - Hide the toolbar.
  - Enable "Auto fill layout height."
  - Adjust background color as needed.
  - Disable "Apply margin to the sides of the layout."
  
- Test to ensure the form works as expected.

Finally, you can share the public dashboard link to new users.

## Final Notes

- **Confirmation Email Styling**: The confirmation email sent to newly registered users uses ThingsBoard's default styling, which cannot be customized via the UI. To modify the styling, you'll need to edit the ThingsBoard source code directly. Alternatively, you can choose to display the activation link on the public dashboard dashboard (requires editing of lambda function), or create a pipeline that sends the email to tenant address, allowing you to forward it to the customer with your own custom styling.

- **WAF Setup**: For enhanced security, consider setting up an AWS Web Application Firewall (WAF) to restrict API access to specific IP addresses. This ensures that only trusted sources can make calls to your API Gateway, protecting against unauthorized access.

- **Mobile-Responsive Widgets**: To improve user experience on mobile devices, you can create additional mobile-responsive widgets in ThingsBoard. This will ensure that your dashboard is accessible and user-friendly across different screen sizes.

