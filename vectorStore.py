import os

from dotenv import load_dotenv
from langchain_community.vectorstores import Cassandra
from cassandra.cluster import Cluster
from langchain_huggingface import HuggingFaceEmbeddings
import urllib3
import cassio
from together import Together


# Load environment variables
load_dotenv()


# Cassandra connection configuration
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", "172.21.0.2")
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "ks_vector")

def init_cassandra():
    # Initialize Cassandra connection
    cluster = Cluster([CASSANDRA_HOST])
    session = cluster.connect()
    
    # Create keyspace in Cassandra
    session.execute(f""" CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
                    WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}""")
    
    return session

def setup_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"  # This is a lightweight, efficient model
    )
    
    # Initialize Cassandra session
    session = init_cassandra()
    
    # Initialize cassio with session and keyspace
    cassio.init(session=session, keyspace=CASSANDRA_KEYSPACE)
    
    # Create vector store
    vector_store = Cassandra(
        embedding=embeddings,
        table_name="document_embeddings",
    )
    return vector_store

def add_texts_to_vectorstore(vector_store, texts):
    vector_store.add_texts(texts)

# Initialize Together client
client = Together()  # auth defaults to os.environ.get("TOGETHER_API_KEY")

def make_llm_request(additional_context):
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[
                {
                    "role": "system",
                    "content": "You help writing well formulated text summary from a given textual input and a question. Limit the response to 20 to 30 words"
                },
                {
                    "role": "user",
                    "content": additional_context
                }
            ],
            max_tokens=256,
            temperature=0,
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error making Together API request: {e}")
        return None



def main():
    # Initialize vector store
    vector_store = setup_vector_store()
    
    # Example text to be imported in to the vectore store
    sample_texts = [
        "The quick brown fox jumps over the lazy dog",
        "The author of Cassandra as a Vector Store is Katerina Doneva",
        "Katerina does not know python programming however she uses AmazonQ to do it!",
        "Mateo also uses AmazonQ"
    ]
    
    # Add texts to vector store
    add_texts_to_vectorstore(vector_store, sample_texts)

    user_question = "Who uses Amazon Q?"
    # user_question = "Who jumped over the dog?"
    search_results = vector_store.similarity_search(user_question, k=2)
    
    print(f"Your question is: {user_question}")
    print(f"What I found in the DB matching this context is:")
    print("-" * 100)
    for doc in search_results:
        print(f"-> {doc.page_content}")
        print("-" * 100)
   
    context = " ".join(doc.page_content for doc in search_results)
    response = make_llm_request("Answer this question: "+user_question+" based on this context "+context)
    print(f"The answer from the LLM on the given context is: {response}")

    # delete the content from the document_embeddings to avoid duplicates when reruning this program from beggining
    cluster = Cluster([CASSANDRA_HOST])
    session = cluster.connect()
    session.execute("TRUNCATE ks_vector.document_embeddings")
    
if __name__ == "__main__":
    main()
