# cassandra-as-vector-store
Simple example of using Apache Cassandra as Vector Store in RAG workflow combined with Free model from Together
## How to get Cassandra as a docker image

Execute this to pull the latest image with Cassandra 5
```bash
docker pull cassandra:latest
```
To create a new user-defined Docker network named "cassandra" execute

```bash
docker network create cassandra
```
Execute this command to create container named cassandra and connect to the previously created network
```bash
docker run --rm -d --name cassandra --hostname cassandra --network cassandra cassandra
```
Get the IP address for CASSANDRA_HOST by doing this. Set this address in the constants CASSANDRA_HOST of the .env file

```bash
docker exec -it cassandra bash
hostname -I
```

### How to start cassandra cqlsh
```bash
docker exec -it cassandra cqlsh
```

execute select command
```bash
cqlsh> SELECT * FROM ks_vector.document_embeddings;
```

The table is empty after each run it is deleted, so you should be seeing something like this:
```bash
 row_id | attributes_blob | body_blob | metadata_s | vector
--------+-----------------+-----------+------------+--------

(0 rows)
```

## Important Notes

> 💡 **Model Information**  
> The implementation uses the 'all-MiniLM-L6-v2' model for creating embeddings

> ⚙️ **Database Configuration**  
> Cassandra keyspace uses SimpleStrategy with replication factor 1

> 🧹 **Cleanup Process**  
> The system automatically cleans up stored embeddings after each run

> 📝 **Response Limitations**  
> LLM responses are limited to 20-30 words

> ⚠️ **Security Warning**  
> SSL verification is disabled for LLM API requests (not recommended for production)



