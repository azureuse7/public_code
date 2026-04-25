# Azure Functions

## References

- [Azure Logic Apps to control Azure Functions](https://medium.com/@abdelhakbahri/start-stop-azure-virtual-machines-using-a-rest-api-and-azure-functions-a62758decc34)
- [YouTube: Azure Functions Tutorial](https://www.youtube.com/watch?v=uBBCA2cJe1k)

---

## 1. What is an Azure Function?

**Azure Functions** is a **serverless** compute service provided by Microsoft Azure. It allows you to run small pieces of code (known as "functions") without having to manage or provision servers explicitly. Azure Functions automatically scales based on demand and charges you only for the compute resources you consume.

### Key Features of Azure Functions

- **Event-Driven:** Functions can be triggered by various events such as HTTP requests, timers, message queues, database changes, and more.
- **Serverless Architecture:** No need to manage infrastructure; focus solely on writing code.
- **Scalability:** Automatically scales out to handle increased load.
- **Flexible Development:** Supports multiple programming languages including Python, C#, JavaScript, and more.
- **Integrated Security:** Easily integrates with Azure Active Directory and other security features.
- **Cost-Effective:** Pay only for the execution time and resources used by your functions.

---

## 2. What is an Azure Function App?

An **Azure Function App** is a container or hosting environment for one or more Azure Functions. It provides the necessary resources and configurations that your functions share, such as:

- **Runtime Settings:** Defines the runtime version and language settings.
- **Environment Variables:** Stores configuration settings and secrets.
- **Scaling Configuration:** Manages how your functions scale in response to demand.
- **Deployment Settings:** Handles deployment methods and source control integrations.

### Benefits of Using a Function App

- **Resource Sharing:** Multiple functions within a Function App share the same resources, making it easier to manage and monitor them collectively.
- **Consistent Configuration:** Apply consistent settings and configurations across all functions in the app.
- **Simplified Deployment:** Deploy multiple functions together, streamlining the deployment process.

---

## 3. How Does an Azure Function App Work?

Azure Function Apps operate based on a trigger and bindings model. Here is a high-level workflow:

1. **Trigger:** An event that initiates the execution of a function (e.g., an HTTP request, a new message in a queue).
2. **Function Code:** The actual code that runs in response to the trigger.
3. **Bindings:** Connectors that allow your function to interact with other services (e.g., reading from or writing to storage accounts or databases).

### Example Workflow in Python

This example shows an Azure Function triggered by an HTTP request that processes some data and returns a response.

#### Scenario

Create an HTTP-triggered Azure Function that receives a JSON payload containing a user's name and returns a personalised greeting.

#### Step-by-Step Workflow

1. **Create a Function App:**
   - Set up a Function App in the Azure Portal or using the Azure CLI.
   - Choose Python as the runtime stack.
2. **Create an HTTP-Triggered Function:**
   - Inside the Function App, create a new function with an HTTP trigger.
3. **Write the Python Code:**
   - Implement the logic to process the incoming request and generate a response.
4. **Configure Bindings (Optional):**
   - If needed, add input/output bindings to interact with other Azure services.
5. **Deploy and Test:**
   - Deploy the function and test it by sending HTTP requests.

#### Detailed Implementation

##### a. Creating the Function App and Function

You can create a Function App and an HTTP-triggered function using the Azure Portal, Azure CLI, or Visual Studio Code with the Azure Functions extension. Here is a simplified approach using the Azure Portal:

1. **Navigate to Azure Portal:** Sign in to the [Azure Portal](https://portal.azure.com/).
2. **Create a Function App:**
   - Click on **"Create a resource"** > **"Compute"** > **"Function App"**.
   - Fill in the required details:
     - **Subscription:** Choose your Azure subscription.
     - **Resource Group:** Create a new one or use an existing group.
     - **Function App Name:** Provide a unique name.
     - **Runtime Stack:** Select **Python**.
     - **Version:** Choose the desired Python version (e.g., Python 3.9).
     - **Region:** Select a region close to your users.
   - Click **"Review + create"** and then **"Create"**.
3. **Add a New Function:**
   - Once the Function App is created, navigate to it.
   - Click on **"Functions"** > **"Add"** > **"HTTP trigger"**.
   - Provide a name for your function (e.g., `GreetUser`) and set the authorisation level (e.g., Function, Anonymous).
   - Click **"Add"**.

##### b. Writing the Python Function Code

Once the function is created, write the Python code:

```python
import logging
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('GreetUser function processed a request.')

    try:
        # Parse JSON body
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON payload.",
            status_code=400
        )

    name = req_body.get('name')

    if name:
        greeting = f"Hello, {name}! Welcome to Azure Functions."
        return func.HttpResponse(
            json.dumps({"greeting": greeting}),
            mimetype="application/json",
            status_code=200
        )
    else:
        return func.HttpResponse(
            "Please pass a name in the JSON payload.",
            status_code=400
        )
```

##### c. Understanding the Code

1. **Imports:**
   - `logging` — for logging information.
   - `json` — for handling JSON data.
   - `azure.functions` — provides types and utilities for Azure Functions.
2. **Function Definition:**
   - `main` is the entry point for the function. It accepts an `HttpRequest` object and returns an `HttpResponse`.
3. **Processing the Request:**
   - Attempts to parse the incoming JSON payload.
   - Extracts the `name` field from the JSON data.
4. **Generating the Response:**
   - If `name` is present, creates a personalised greeting and returns it as a JSON response with a `200 OK` status.
   - If `name` is missing or the JSON is invalid, returns an error message with a `400 Bad Request` status.

##### d. Testing the Function

1. **Obtain the Function URL:**
   - In the Azure Portal, navigate to your function (`GreetUser`).
   - Click on **"Get Function URL"** and copy the URL.

2. **Send an HTTP Request** using `curl`, Postman, or any HTTP client:

```bash
curl -X POST \
  https://<your-function-app>.azurewebsites.net/api/GreetUser \
  -H 'Content-Type: application/json' \
  -d '{"name": "Alice"}'
```

**Expected Response:**

```json
{
  "greeting": "Hello, Alice! Welcome to Azure Functions."
}
```

**Error Handling — Missing Name:**

```bash
curl -X POST \
  https://<your-function-app>.azurewebsites.net/api/GreetUser \
  -H 'Content-Type: application/json' \
  -d '{}'
```

Response:

```
Please pass a name in the JSON payload.
```

**Error Handling — Invalid JSON:**

```bash
curl -X POST \
  https://<your-function-app>.azurewebsites.net/api/GreetUser \
  -H 'Content-Type: application/json' \
  -d 'Invalid JSON'
```

Response:

```
Invalid JSON payload.
```

---

## 4. Additional Components and Considerations

### a. Triggers and Bindings

- **Triggers:** Initiate the execution of a function (e.g., HTTP requests, timer schedules, queue messages).
- **Bindings:** Declaratively connect to other services without managing connections explicitly (e.g., Azure Blob Storage, Cosmos DB).

### b. Deployment Options

You can deploy Azure Functions using various methods:

- **Azure Portal:** Directly edit and test your code in the browser.
- **Visual Studio Code:** Use the Azure Functions extension for development and deployment.
- **Azure CLI:** Deploy via command-line interfaces.
- **CI/CD Pipelines:** Integrate with GitHub Actions, Azure DevOps, or other CI/CD tools.

### c. Monitoring and Logging

Azure Functions integrates with **Azure Monitor** and **Application Insights** to provide detailed logging, performance metrics, and error tracking, allowing you to monitor the health and performance of your functions effectively.

### d. Pricing Models

Azure Functions offers different pricing plans:

- **Consumption Plan:** Pay only for the resources consumed during function execution. Automatically scales and is ideal for variable workloads.
- **Premium Plan:** Provides enhanced performance, VNet connectivity, and more predictable scaling. Suitable for enterprise-grade applications.
- **Dedicated (App Service) Plan:** Runs functions on dedicated VMs. Useful if you already have existing App Service resources.

---

## 5. Conclusion

**Azure Functions** and **Function Apps** provide a powerful and flexible way to build scalable, event-driven applications without the overhead of managing infrastructure. By leveraging triggers and bindings, you can integrate seamlessly with a wide array of Azure services and external systems.

### Benefits Illustrated in the Example

- **Simplicity:** Focused on writing the core logic without worrying about server management.
- **Scalability:** Automatically handles varying loads, ensuring responsiveness.
- **Cost-Efficiency:** Pay only for the compute resources you use.
- **Flexibility:** Easily integrate with other services and extend functionality as needed.

Whether you are building APIs, processing data, automating tasks, or integrating systems, Azure Functions offer a robust platform to develop and deploy your solutions efficiently.
