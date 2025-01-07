#### Azure Cosmos DB 
Azure Cosmos DB is Microsoft's globally distributed, multi-model database service designed to provide high availability, low latency, and scalable performance for modern applications. It supports multiple data models, including document, key-value, graph, and column-family, making it versatile for a wide range of use cases.

**What is Azure Cosmos DB?**

Azure Cosmos DB is a fully managed NoSQL database service that offers the following key features:

1. **Global Distribution:** Replicate your data across any number of Azure regions to achieve high availability and low latency for your users worldwide.
1. **Multi-Model Support:** Supports various data models such as:
   1. **Document** (e.g., JSON)
   1. **Key-Value**
   1. **Graph** (e.g., Gremlin)
   1. **Column-Family** (e.g., Cassandra)
1. **Elastic Scalability:** Automatically scales throughput and storage based on your application's needs.
1. **Low Latency:** Guarantees single-digit millisecond response times for both reads and writes at the 99th percentile worldwide.
1. **Comprehensive SLAs:** Offers industry-leading SLAs for availability, throughput, consistency, and latency.
1. **Multiple Consistency Models:** Provides five well-defined consistency levels to balance between performance and data consistency:
   1. Strong
   1. Bounded Staleness
   1. Session
   1. Consistent Prefix
   1. Eventual

**How Does Azure Cosmos DB Work in Azure?**

Azure Cosmos DB operates as a globally distributed database service with a partitioned architecture to handle large volumes of data and high transaction rates. Here's a high-level overview of its workflow:

1. **Data Partitioning:**
   1. **Containers:** The highest level of data organization, similar to tables in relational databases.
   1. **Partitions:** Containers are divided into multiple physical partitions based on a partition key, which helps distribute data and load evenly.
1. **Replication:**
   1. Data is replicated across multiple Azure regions to ensure high availability and low latency.
   1. You can configure the number of replicas and regions based on your application's requirements.
1. **Consistency:**
   1. Choose a consistency model that suits your application’s needs to balance between performance and data accuracy.
1. **Throughput Management:**
   1. Provisioned throughputs are measured in Request Units per second (RUs/s), which abstract the cost of database operations.
   1. Cosmos DB automatically manages the distribution of RUs across partitions.
1. **APIs:**
   1. Cosmos DB provides multiple APIs to interact with the database, including SQL (Core), MongoDB, Cassandra, Gremlin (graph), and Table (Azure Table storage).

**Example Workflow in Python**

Below is a step-by-step example of how to interact with Azure Cosmos DB using Python. This example demonstrates creating a database and container, inserting items, and querying data using the SQL API.

**Prerequisites**

1. **Azure Account:** You need an active Azure subscription. If you don't have one, you can create a [free account](https://azure.microsoft.com/free/).
1. **Azure Cosmos DB Account:** Create an Azure Cosmos DB account via the Azure Portal. Choose the SQL (Core) API for this example.
1. **Python Environment:** Ensure you have Python 3.6 or later installed.
1. **Install Azure Cosmos SDK:**
```python
   bash

   pip install azure-cosmos
```
**Step 1: Import Required Libraries**
```python
python

from azure.cosmos import CosmosClient, PartitionKey, exceptions

import os
```
**Step 2: Set Up Cosmos DB Client**

You need the **URI** and **Primary Key** from your Cosmos DB account. You can find these in the Azure Portal under the "Keys" section of your Cosmos DB account.
```python
python

\# Replace with your actual URI and Primary Key

COSMOS\_URI = "https://<your-cosmosdb-account>.documents.azure.com:443/"

COSMOS\_KEY = "<your-primary-key>"

\# Initialize the Cosmos client

client = CosmosClient(COSMOS\_URI, COSMOS\_KEY)
```
**Step 3: Create a Database**
```python
python


database\_name = 'HouseExtensionDB'

try:

`    `database = client.create\_database\_if\_not\_exists(id=database\_name)

`    `print(f"Database '{database\_name}' created or already exists.")

except exceptions.CosmosResourceExistsError:

`    `database = client.get\_database\_client(database\_name)

`    `print(f"Database '{database\_name}' already exists.")
```
**Step 4: Create a Container**

A container is a collection of documents. Define a **partition key** to distribute data effectively. For example, using category as a partition key.
```python
python

container\_name = 'Projects'

try:

`    `container = database.create\_container\_if\_not\_exists(

`        `id=container\_name,

`        `partition\_key=PartitionKey(path="/category"),

`        `offer\_throughput=400

`    `)

`    `print(f"Container '{container\_name}' created or already exists.")

except exceptions.CosmosResourceExistsError:

`    `container = database.get\_container\_client(container\_name)

`    `print(f"Container '{container\_name}' already exists.")
```
**Step 5: Insert Items into the Container**

Let's insert some project-related documents.
```python
python


projects = [

`    `{

`        `'id': '1',

`        `'name': 'Kitchen Extension',

`        `'category': 'Renovation',

`        `'budget': 15000,

`        `'status': 'In Progress'

`    `},

`    `{

`        `'id': '2',

`        `'name': 'Living Room Addition',

`        `'category': 'Extension',

`        `'budget': 25000,

`        `'status': 'Planned'

`    `},

`    `{

`        `'id': '3',

`        `'name': 'Bathroom Upgrade',

`        `'category': 'Renovation',

`        `'budget': 8000,

`        `'status': 'Completed'

`    `}

]

for project in projects:

`    `try:

`        `container.create\_item(body=project)

`        `print(f"Inserted project '{project['name']}'")

`    `except exceptions.CosmosResourceExistsError:

`        `print(f"Project '{project['name']}' already exists.")
```
**Step 6: Query Items from the Container**

Retrieve all projects in the "Renovation" category.
```python
python


query = "SELECT \* FROM Projects p WHERE p.category = @category"

parameters = [

`    `{ "name": "@category", "value": "Renovation" }

]

items = list(container.query\_items(

`    `query=query,

`    `parameters=parameters,

`    `enable\_cross\_partition\_query=True

))

print("Renovation Projects:")

for item in items:

`    `print(f"- {item['name']} (Budget: ${item['budget']})")
```
**Step 7: Update an Item**

Update the status of a project.
```python
python


\# Fetch the item to update

project\_id = '2'

partition\_key = 'Extension'

try:

`    `item = container.read\_item(item=project\_id, partition\_key=partition\_key)

`    `item['status'] = 'In Progress'

`    `container.upsert\_item(body=item)

`    `print(f"Updated project '{item['name']}' status to '{item['status']}'")

except exceptions.CosmosResourceNotFoundError:

`    `print(f"Project with id '{project\_id}' not found.")
```
**Step 8: Delete an Item**

Delete a project from the container.
```python
python


project\_id = '3'

partition\_key = 'Renovation'

try:

`    `container.delete\_item(item=project\_id, partition\_key=partition\_key)

`    `print(f"Deleted project with id '{project\_id}'")

except exceptions.CosmosResourceNotFoundError:

`    `print(f"Project with id '{project\_id}' not found.")
```
**Full Example Code**

Here’s the complete Python script combining all the steps above:
```python
python


from azure.cosmos import CosmosClient, PartitionKey, exceptions

import os

\# Replace with your actual URI and Primary Key

COSMOS\_URI = "https://<your-cosmosdb-account>.documents.azure.com:443/"

COSMOS\_KEY = "<your-primary-key>"

\# Initialize the Cosmos client

client = CosmosClient(COSMOS\_URI, COSMOS\_KEY)

\# Create/Get Database

database\_name = 'HouseExtensionDB'

try:

`    `database = client.create\_database\_if\_not\_exists(id=database\_name)

`    `print(f"Database '{database\_name}' created or already exists.")

except exceptions.CosmosResourceExistsError:

`    `database = client.get\_database\_client(database\_name)

`    `print(f"Database '{database\_name}' already exists.")

\# Create/Get Container

container\_name = 'Projects'

try:

`    `container = database.create\_container\_if\_not\_exists(

`        `id=container\_name,

`        `partition\_key=PartitionKey(path="/category"),

`        `offer\_throughput=400

`    `)

`    `print(f"Container '{container\_name}' created or already exists.")

except exceptions.CosmosResourceExistsError:

`    `container = database.get\_container\_client(container\_name)

`    `print(f"Container '{container\_name}' already exists.")

\# Insert Items

projects = [

`    `{

`        `'id': '1',

`        `'name': 'Kitchen Extension',

`        `'category': 'Renovation',

`        `'budget': 15000,

`        `'status': 'In Progress'

`    `},

`    `{

`        `'id': '2',

`        `'name': 'Living Room Addition',

`        `'category': 'Extension',

`        `'budget': 25000,

`        `'status': 'Planned'

`    `},

`    `{

`        `'id': '3',

`        `'name': 'Bathroom Upgrade',

`        `'category': 'Renovation',

`        `'budget': 8000,

`        `'status': 'Completed'

`    `}

]

for project in projects:

`    `try:

`        `container.create\_item(body=project)

`        `print(f"Inserted project '{project['name']}'")

`    `except exceptions.CosmosResourceExistsError:

`        `print(f"Project '{project['name']}' already exists.")

\# Query Items

query = "SELECT \* FROM Projects p WHERE p.category = @category"

parameters = [

`    `{ "name": "@category", "value": "Renovation" }

]

items = list(container.query\_items(

`    `query=query,

`    `parameters=parameters,

`    `enable\_cross\_partition\_query=True

))

print("\nRenovation Projects:")

for item in items:

`    `print(f"- {item['name']} (Budget: ${item['budget']})")

\# Update an Item

project\_id = '2'

partition\_key = 'Extension'

try:

`    `item = container.read\_item(item=project\_id, partition\_key=partition\_key)

`    `item['status'] = 'In Progress'

`    `container.upsert\_item(body=item)

`    `print(f"\nUpdated project '{item['name']}' status to '{item['status']}'")

except exceptions.CosmosResourceNotFoundError:

`    `print(f"Project with id '{project\_id}' not found.")

\# Delete an Item

project\_id = '3'

partition\_key = 'Renovation'

try:

`    `container.delete\_item(item=project\_id, partition\_key=partition\_key)

`    `print(f"Deleted project with id '{project\_id}'")

except exceptions.CosmosResourceNotFoundError:

`    `print(f"Project with id '{project\_id}' not found.")
```
**Running the Example**

1. **Set Up Credentials:**
   1. Replace COSMOS\_URI and COSMOS\_KEY with your actual Azure Cosmos DB account URI and Primary Key.
2. **Execute the Script:**
```python
   bash


   python cosmosdb\_example.py
```
3. **Expected Output:**
```python
   bash

   Database 'HouseExtensionDB' created or already exists.

   Container 'Projects' created or already exists.

   Inserted project 'Kitchen Extension'

   Inserted project 'Living Room Addition'

   Inserted project 'Bathroom Upgrade'

   Renovation Projects:

   - Kitchen Extension (Budget: $15000)

   - Bathroom Upgrade (Budget: $8000)

   Updated project 'Living Room Addition' status to 'In Progress'

   Deleted project with id '3'
```
**Conclusion**

Azure Cosmos DB is a powerful, flexible, and globally distributed database service that caters to a wide range of application needs. Its support for multiple data models, combined with high availability and scalability, makes it an excellent choice for modern, cloud-native applications.

The Python example provided demonstrates basic operations such as creating databases and containers, inserting, querying, updating, and deleting items. Azure Cosmos DB’s SDKs support various programming languages, enabling seamless integration into your preferred development stack.

For more advanced use cases, consider exploring features like:

- **Change Feed:** To react to changes in your data in real-time.
- **Stored Procedures, Triggers, and UDFs:** For server-side logic.
- **Time to Live (TTL):** For automatic data expiration.
- **Integration with Azure Functions:** To build serverless applications.

To dive deeper, refer to the [Azure Cosmos DB documentation](https://docs.microsoft.com/azure/cosmos-db/) and explore tutorials and best practices to optimize your database for performance and cost.

