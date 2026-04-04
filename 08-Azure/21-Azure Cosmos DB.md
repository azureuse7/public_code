# Azure Cosmos DB

Azure Cosmos DB is Microsoft's globally distributed, multi-model database service designed to provide high availability, low latency, and scalable performance for modern applications. It supports multiple data models, including document, key-value, graph, and column-family, making it versatile for a wide range of use cases.

## What is Azure Cosmos DB?

Azure Cosmos DB is a fully managed NoSQL database service that offers the following key features:

1. **Global Distribution:** Replicate your data across any number of Azure regions to achieve high availability and low latency for users worldwide.
2. **Multi-Model Support:** Supports various data models such as:
   - Document (e.g., JSON)
   - Key-Value
   - Graph (e.g., Gremlin)
   - Column-Family (e.g., Cassandra)
3. **Elastic Scalability:** Automatically scales throughput and storage based on your application's needs.
4. **Low Latency:** Guarantees single-digit millisecond response times for both reads and writes at the 99th percentile worldwide.
5. **Comprehensive SLAs:** Offers industry-leading SLAs for availability, throughput, consistency, and latency.
6. **Multiple Consistency Models:** Provides five well-defined consistency levels to balance between performance and data consistency:
   - Strong
   - Bounded Staleness
   - Session
   - Consistent Prefix
   - Eventual

## How Does Azure Cosmos DB Work in Azure?

Azure Cosmos DB operates as a globally distributed database service with a partitioned architecture to handle large volumes of data and high transaction rates. Here is a high-level overview of its workflow:

1. **Data Partitioning:**
   - **Containers:** The highest level of data organisation, similar to tables in relational databases.
   - **Partitions:** Containers are divided into multiple physical partitions based on a partition key, which helps distribute data and load evenly.
2. **Replication:**
   - Data is replicated across multiple Azure regions to ensure high availability and low latency.
   - You can configure the number of replicas and regions based on your application's requirements.
3. **Consistency:**
   - Choose a consistency model that suits your application's needs to balance between performance and data accuracy.
4. **Throughput Management:**
   - Provisioned throughput is measured in Request Units per second (RU/s), which abstracts the cost of database operations.
   - Cosmos DB automatically manages the distribution of RUs across partitions.
5. **APIs:**
   - Cosmos DB provides multiple APIs to interact with the database, including SQL (Core), MongoDB, Cassandra, Gremlin (graph), and Table (Azure Table Storage).

## Example Workflow in Python

Below is a step-by-step example of how to interact with Azure Cosmos DB using Python. This example demonstrates creating a database and container, inserting items, and querying data using the SQL API.

### Prerequisites

1. **Azure Account:** You need an active Azure subscription. If you don't have one, you can create a [free account](https://azure.microsoft.com/free/).
2. **Azure Cosmos DB Account:** Create an Azure Cosmos DB account via the Azure Portal. Choose the SQL (Core) API for this example.
3. **Python Environment:** Ensure you have Python 3.6 or later installed.
4. **Install the Azure Cosmos SDK:**

```bash
pip install azure-cosmos
```

### Step 1: Import Required Libraries

```python
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import os
```

### Step 2: Set Up the Cosmos DB Client

You need the **URI** and **Primary Key** from your Cosmos DB account. You can find these in the Azure Portal under the **Keys** section of your Cosmos DB account.

```python
# Replace with your actual URI and Primary Key
COSMOS_URI = "https://<your-cosmosdb-account>.documents.azure.com:443/"
COSMOS_KEY = "<your-primary-key>"

# Initialize the Cosmos client
client = CosmosClient(COSMOS_URI, COSMOS_KEY)
```

### Step 3: Create a Database

```python
database_name = 'HouseExtensionDB'

try:
    database = client.create_database_if_not_exists(id=database_name)
    print(f"Database '{database_name}' created or already exists.")
except exceptions.CosmosResourceExistsError:
    database = client.get_database_client(database_name)
    print(f"Database '{database_name}' already exists.")
```

### Step 4: Create a Container

A container is a collection of documents. Define a **partition key** to distribute data effectively. For example, using `category` as the partition key.

```python
container_name = 'Projects'

try:
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/category"),
        offer_throughput=400
    )
    print(f"Container '{container_name}' created or already exists.")
except exceptions.CosmosResourceExistsError:
    container = database.get_container_client(container_name)
    print(f"Container '{container_name}' already exists.")
```

### Step 5: Insert Items into the Container

Let's insert some project-related documents.

```python
projects = [
    {
        'id': '1',
        'name': 'Kitchen Extension',
        'category': 'Renovation',
        'budget': 15000,
        'status': 'In Progress'
    },
    {
        'id': '2',
        'name': 'Living Room Addition',
        'category': 'Extension',
        'budget': 25000,
        'status': 'Planned'
    },
    {
        'id': '3',
        'name': 'Bathroom Upgrade',
        'category': 'Renovation',
        'budget': 8000,
        'status': 'Completed'
    }
]

for project in projects:
    try:
        container.create_item(body=project)
        print(f"Inserted project '{project['name']}'")
    except exceptions.CosmosResourceExistsError:
        print(f"Project '{project['name']}' already exists.")
```

### Step 6: Query Items from the Container

Retrieve all projects in the "Renovation" category.

```python
query = "SELECT * FROM Projects p WHERE p.category = @category"

parameters = [
    { "name": "@category", "value": "Renovation" }
]

items = list(container.query_items(
    query=query,
    parameters=parameters,
    enable_cross_partition_query=True
))

print("Renovation Projects:")
for item in items:
    print(f"- {item['name']} (Budget: ${item['budget']})")
```

### Step 7: Update an Item

Update the status of a project.

```python
# Fetch the item to update
project_id = '2'
partition_key = 'Extension'

try:
    item = container.read_item(item=project_id, partition_key=partition_key)
    item['status'] = 'In Progress'
    container.upsert_item(body=item)
    print(f"Updated project '{item['name']}' status to '{item['status']}'")
except exceptions.CosmosResourceNotFoundError:
    print(f"Project with id '{project_id}' not found.")
```

### Step 8: Delete an Item

Delete a project from the container.

```python
project_id = '3'
partition_key = 'Renovation'

try:
    container.delete_item(item=project_id, partition_key=partition_key)
    print(f"Deleted project with id '{project_id}'")
except exceptions.CosmosResourceNotFoundError:
    print(f"Project with id '{project_id}' not found.")
```

## Full Example Code

Here is the complete Python script combining all the steps above:

```python
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import os

# Replace with your actual URI and Primary Key
COSMOS_URI = "https://<your-cosmosdb-account>.documents.azure.com:443/"
COSMOS_KEY = "<your-primary-key>"

# Initialize the Cosmos client
client = CosmosClient(COSMOS_URI, COSMOS_KEY)

# Create/Get Database
database_name = 'HouseExtensionDB'

try:
    database = client.create_database_if_not_exists(id=database_name)
    print(f"Database '{database_name}' created or already exists.")
except exceptions.CosmosResourceExistsError:
    database = client.get_database_client(database_name)
    print(f"Database '{database_name}' already exists.")

# Create/Get Container
container_name = 'Projects'

try:
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/category"),
        offer_throughput=400
    )
    print(f"Container '{container_name}' created or already exists.")
except exceptions.CosmosResourceExistsError:
    container = database.get_container_client(container_name)
    print(f"Container '{container_name}' already exists.")

# Insert Items
projects = [
    {
        'id': '1',
        'name': 'Kitchen Extension',
        'category': 'Renovation',
        'budget': 15000,
        'status': 'In Progress'
    },
    {
        'id': '2',
        'name': 'Living Room Addition',
        'category': 'Extension',
        'budget': 25000,
        'status': 'Planned'
    },
    {
        'id': '3',
        'name': 'Bathroom Upgrade',
        'category': 'Renovation',
        'budget': 8000,
        'status': 'Completed'
    }
]

for project in projects:
    try:
        container.create_item(body=project)
        print(f"Inserted project '{project['name']}'")
    except exceptions.CosmosResourceExistsError:
        print(f"Project '{project['name']}' already exists.")

# Query Items
query = "SELECT * FROM Projects p WHERE p.category = @category"

parameters = [
    { "name": "@category", "value": "Renovation" }
]

items = list(container.query_items(
    query=query,
    parameters=parameters,
    enable_cross_partition_query=True
))

print("\nRenovation Projects:")
for item in items:
    print(f"- {item['name']} (Budget: ${item['budget']})")

# Update an Item
project_id = '2'
partition_key = 'Extension'

try:
    item = container.read_item(item=project_id, partition_key=partition_key)
    item['status'] = 'In Progress'
    container.upsert_item(body=item)
    print(f"\nUpdated project '{item['name']}' status to '{item['status']}'")
except exceptions.CosmosResourceNotFoundError:
    print(f"Project with id '{project_id}' not found.")

# Delete an Item
project_id = '3'
partition_key = 'Renovation'

try:
    container.delete_item(item=project_id, partition_key=partition_key)
    print(f"Deleted project with id '{project_id}'")
except exceptions.CosmosResourceNotFoundError:
    print(f"Project with id '{project_id}' not found.")
```

## Running the Example

1. **Set Up Credentials:** Replace `COSMOS_URI` and `COSMOS_KEY` with your actual Azure Cosmos DB account URI and Primary Key.

2. **Execute the Script:**

```bash
python cosmosdb_example.py
```

3. **Expected Output:**

```
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

## Conclusion

Azure Cosmos DB is a powerful, flexible, and globally distributed database service that caters to a wide range of application needs. Its support for multiple data models, combined with high availability and scalability, makes it an excellent choice for modern, cloud-native applications.

The Python example above demonstrates basic CRUD operations: creating databases and containers, inserting, querying, updating, and deleting items. Azure Cosmos DB's SDKs support various programming languages, enabling seamless integration into your preferred development stack.

For more advanced use cases, consider exploring:

- **Change Feed:** React to changes in your data in real time.
- **Stored Procedures, Triggers, and UDFs:** For server-side logic.
- **Time to Live (TTL):** For automatic data expiration.
- **Integration with Azure Functions:** To build serverless applications.

For further reading, refer to the [Azure Cosmos DB documentation](https://docs.microsoft.com/azure/cosmos-db/).
