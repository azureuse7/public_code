# Azure Table Storage

Azure Table Storage is a highly scalable, NoSQL cloud storage solution provided by Microsoft Azure. It is designed to store large amounts of structured, non-relational data, making it ideal for applications that require quick access to vast datasets without the overhead of a traditional relational database.

## What is Azure Table Storage?

**Azure Table Storage** is part of the Azure Storage suite, which also includes Blob Storage, Queue Storage, and File Storage. It offers a key-attribute store with a schema-less design, enabling developers to store and retrieve large volumes of data efficiently.

### Key Components

1. **Tables:** The highest-level container that holds entities. Each storage account can have multiple tables.
2. **Entities:** Individual records within a table, similar to rows in a relational database.
3. **Properties:** Attributes of an entity, analogous to columns in a relational database. Each property has a name, value, and data type.
4. **PartitionKey:** A property that defines the partition to which an entity belongs. It is used to distribute data across storage nodes, ensuring scalability and performance.
5. **RowKey:** A unique identifier for an entity within a partition. Combined with the `PartitionKey`, it forms a unique key for each entity.

### Key Features

- **Scalability:** Handles massive amounts of data with high availability and durability.
- **Flexibility:** Schema-less design allows for varied data structures within the same table.
- **Performance:** Optimised for fast read and write operations.
- **Cost-Effective:** Pay-as-you-go pricing model ensures you only pay for what you use.
- **Integration:** Seamlessly integrates with other Azure services and supports RESTful APIs.

### Common Use Cases

- **Storing Metadata:** Ideal for storing metadata for applications like media repositories.
- **User Data:** Managing user profiles and session information.
- **Device Data:** Storing telemetry and sensor data from IoT devices.
- **Logging and Auditing:** Maintaining logs and audit trails for applications.

## How Azure Table Storage Works: A Python Workflow Example

To interact with Azure Table Storage using Python, you use the `azure-data-tables` SDK. Below is a step-by-step guide demonstrating common operations: creating a table, inserting entities, querying data, updating entities, and deleting entities.

### Prerequisites

1. **Azure Account:** Ensure you have an active Azure subscription. If not, you can create a free account [here](https://azure.microsoft.com/free/).
2. **Azure Storage Account:** Create a Storage Account via the Azure Portal. Note down the **Connection String** from the **Access Keys** section.
3. **Python Environment:** Ensure Python is installed on your machine. You can download it from [python.org](https://www.python.org/downloads/).
4. **Azure Data Tables SDK:** Install the SDK using `pip`:

```bash
pip install azure-data-tables
```

### Step-by-Step Workflow

#### 1. Import Required Libraries

```python
from azure.data.tables import TableServiceClient, TableClient, UpdateMode
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import os
```

#### 2. Set Up Connection

It is best practice to store your connection string securely in environment variables.

```python
# Retrieve the connection string from an environment variable
connection_string = os.getenv('AZURE_TABLE_STORAGE_CONNECTION_STRING')

if not connection_string:
    raise ValueError("Please set the AZURE_TABLE_STORAGE_CONNECTION_STRING environment variable.")
```

#### 3. Create a Table

```python
def create_table(table_name):
    try:
        # Initialize TableServiceClient
        service = TableServiceClient.from_connection_string(conn_str=connection_string)

        # Create the table
        table = service.create_table(table_name)
        print(f"Table '{table_name}' created successfully.")
    except ResourceExistsError:
        print(f"Table '{table_name}' already exists.")
    except Exception as e:
        print(f"Error creating table: {e}")

# Example usage
create_table("Customers")
```

#### 4. Insert an Entity

```python
def insert_entity(table_name, entity):
    try:
        table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
        table_client.create_entity(entity=entity)
        print(f"Entity inserted: {entity}")
    except ResourceExistsError:
        print("Entity already exists.")
    except Exception as e:
        print(f"Error inserting entity: {e}")

# Example entity
customer = {
    'PartitionKey': 'Customers',
    'RowKey': 'C001',
    'Name': 'John Doe',
    'Email': 'johndoe@example.com',
    'PhoneNumber': '123-456-7890'
}

# Example usage
insert_entity("Customers", customer)
```

#### 5. Query Entities

```python
def query_entities(table_name, partition_key):
    try:
        table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
        entities = table_client.query_entities(f"PartitionKey eq '{partition_key}'")

        print(f"Entities in partition '{partition_key}':")
        for entity in entities:
            print(entity)
    except ResourceNotFoundError:
        print(f"Table '{table_name}' not found.")
    except Exception as e:
        print(f"Error querying entities: {e}")

# Example usage
query_entities("Customers", "Customers")
```

#### 6. Update an Entity

```python
def update_entity(table_name, partition_key, row_key, updated_properties):
    try:
        table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
        # Retrieve the existing entity
        entity = table_client.get_entity(partition_key=partition_key, row_key=row_key)

        # Update properties
        for key, value in updated_properties.items():
            entity[key] = value

        # Update the entity in the table
        table_client.update_entity(mode=UpdateMode.MERGE, entity=entity)
        print(f"Entity '{row_key}' updated successfully.")
    except ResourceNotFoundError:
        print(f"Entity with PartitionKey='{partition_key}' and RowKey='{row_key}' not found.")
    except Exception as e:
        print(f"Error updating entity: {e}")

# Example usage
updated_info = {
    'Email': 'john.doe@newdomain.com',
    'PhoneNumber': '098-765-4321'
}

update_entity("Customers", "Customers", "C001", updated_info)
```

#### 7. Delete an Entity

```python
def delete_entity(table_name, partition_key, row_key):
    try:
        table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
        table_client.delete_entity(partition_key=partition_key, row_key=row_key)
        print(f"Entity '{row_key}' deleted successfully.")
    except ResourceNotFoundError:
        print(f"Entity with PartitionKey='{partition_key}' and RowKey='{row_key}' not found.")
    except Exception as e:
        print(f"Error deleting entity: {e}")

# Example usage
delete_entity("Customers", "Customers", "C001")
```

#### 8. Delete a Table (Optional)

```python
def delete_table(table_name):
    try:
        service = TableServiceClient.from_connection_string(conn_str=connection_string)
        service.delete_table(table_name)
        print(f"Table '{table_name}' deleted successfully.")
    except ResourceNotFoundError:
        print(f"Table '{table_name}' does not exist.")
    except Exception as e:
        print(f"Error deleting table: {e}")

# Example usage
delete_table("Customers")
```

### Full Example Script

Here is how you might combine all the above functions into a single script:

```python
import os
from azure.data.tables import TableServiceClient, TableClient, UpdateMode
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

# Retrieve the connection string from an environment variable
connection_string = os.getenv('AZURE_TABLE_STORAGE_CONNECTION_STRING')

if not connection_string:
    raise ValueError("Please set the AZURE_TABLE_STORAGE_CONNECTION_STRING environment variable.")

def create_table(table_name):
    try:
        service = TableServiceClient.from_connection_string(conn_str=connection_string)
        table = service.create_table(table_name)
        print(f"Table '{table_name}' created successfully.")
    except ResourceExistsError:
        print(f"Table '{table_name}' already exists.")
    except Exception as e:
        print(f"Error creating table: {e}")

def insert_entity(table_name, entity):
    try:
        table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
        table_client.create_entity(entity=entity)
        print(f"Entity inserted: {entity}")
    except ResourceExistsError:
        print("Entity already exists.")
    except Exception as e:
        print(f"Error inserting entity: {e}")

def query_entities(table_name, partition_key):
    try:
        table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
        entities = table_client.query_entities(f"PartitionKey eq '{partition_key}'")

        print(f"Entities in partition '{partition_key}':")
        for entity in entities:
            print(entity)
    except ResourceNotFoundError:
        print(f"Table '{table_name}' not found.")
    except Exception as e:
        print(f"Error querying entities: {e}")

def update_entity(table_name, partition_key, row_key, updated_properties):
    try:
        table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
        entity = table_client.get_entity(partition_key=partition_key, row_key=row_key)

        for key, value in updated_properties.items():
            entity[key] = value

        table_client.update_entity(mode=UpdateMode.MERGE, entity=entity)
        print(f"Entity '{row_key}' updated successfully.")
    except ResourceNotFoundError:
        print(f"Entity with PartitionKey='{partition_key}' and RowKey='{row_key}' not found.")
    except Exception as e:
        print(f"Error updating entity: {e}")

def delete_entity(table_name, partition_key, row_key):
    try:
        table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
        table_client.delete_entity(partition_key=partition_key, row_key=row_key)
        print(f"Entity '{row_key}' deleted successfully.")
    except ResourceNotFoundError:
        print(f"Entity with PartitionKey='{partition_key}' and RowKey='{row_key}' not found.")
    except Exception as e:
        print(f"Error deleting entity: {e}")

def delete_table(table_name):
    try:
        service = TableServiceClient.from_connection_string(conn_str=connection_string)
        service.delete_table(table_name)
        print(f"Table '{table_name}' deleted successfully.")
    except ResourceNotFoundError:
        print(f"Table '{table_name}' does not exist.")
    except Exception as e:
        print(f"Error deleting table: {e}")

# Example usage
if __name__ == "__main__":
    table_name = "Customers"

    # Create Table
    create_table(table_name)

    # Insert Entity
    customer = {
        'PartitionKey': 'Customers',
        'RowKey': 'C001',
        'Name': 'John Doe',
        'Email': 'johndoe@example.com',
        'PhoneNumber': '123-456-7890'
    }
    insert_entity(table_name, customer)

    # Query Entities
    query_entities(table_name, 'Customers')

    # Update Entity
    updated_info = {
        'Email': 'john.doe@newdomain.com',
        'PhoneNumber': '098-765-4321'
    }
    update_entity(table_name, 'Customers', 'C001', updated_info)

    # Query Entities After Update
    query_entities(table_name, 'Customers')

    # Delete Entity
    delete_entity(table_name, 'Customers', 'C001')

    # Delete Table
    delete_table(table_name)
```

## Best Practices

1. **Secure Your Connection String:** Avoid hardcoding sensitive information. Use environment variables or Azure Key Vault to manage secrets.
2. **Efficient Partitioning:** Choose an appropriate `PartitionKey` to distribute load evenly and optimise query performance.
3. **Handle Exceptions Gracefully:** Implement robust error handling to manage scenarios like network failures or resource constraints.
4. **Optimise Queries:** Retrieve only the necessary properties to reduce latency and cost.
5. **Monitor and Scale:** Use Azure Monitor to track performance and scale your storage account as needed.

## Additional Resources

- [Azure Table Storage Documentation](https://learn.microsoft.com/azure/storage/tables/table-storage-overview)
- [Azure Data Tables SDK for Python](https://learn.microsoft.com/python/api/overview/azure/data-tables-readme?view=azure-python)
- [Azure Storage Pricing](https://azure.microsoft.com/pricing/details/storage/tables/)
