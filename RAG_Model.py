# Importing necessary libraries and modules
import textwrap
import os
from openai import OpenAI  # Importing OpenAI library for text generation
from pinecone import Pinecone  # Importing Pinecone library for vector indexing

# Initializing OpenAI with API key
os.environ['OPENAI_API_KEY'] = '------'
client = OpenAI()  # Initializing OpenAI client

# Initializing Pinecone with API key and environment
os.environ['PINECONE_API_KEY'] = '-----'
os.environ['PINECONE_ENVIRONMENT'] = 'gcp-starter'
api_key = os.getenv('PINECONE_API_KEY')
env = os.getenv('PINECONE_ENVIRONMENT')
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

# Connecting to an existing Pinecone index
index = pc.Index('my-solar-system')
index.describe_index_stats()  # Displaying index statistics

# Function to get text embeddings using OpenAI
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")  # Removing newline characters
    return client.embeddings.create(input=text, model=model).data[0].embedding

# Function to retrieve data from Pinecone based on a query
def generate_augmented_query(query, embed_model='text-embedding-ada-002', k=5):
    xq = get_embedding(query, model=embed_model)  # Get embedding for the query
    res = index.query(vector=xq, top_k=k, include_metadata=True)  # Query the index
    contexts = [item['metadata']['text'] for item in res['matches']]  # Extract text contexts from results
    ref = [item['metadata']['ref'] for item in res['matches']]  # Extract references from results
    return "\n\n---\n\n".join(contexts) + "\n\n-----\n\n" + query, "\n---\n".join(ref) + "\n-----\n" + query

# Function to interact with GPT-3 for generating responses
def ask_gpt(system_prompt, user_prompt, model='gpt-3.5-turbo'):
    temperature_ = 0.7  # Tuning parameter for text generation
    completion = client.chat.completions.create(model=model, temperature=temperature_, messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}])
    lines = (completion.choices[0].message.content).split("\n")  # Splitting the generated text into lines
    lists = (textwrap.TextWrapper(width=90, break_long_words=False).wrap(line) for line in lines)  # Wrapping lines based on a maximum width
    return "\n".join("\n".join(list) for list in lists)  # Joining the wrapped lines into a single string

# Function to generate responses using a combination of retrieved data and GPT-3
def rag_response(query):
    embed_model = 'text-embedding-ada-002'  # Embedding model for querying Pinecone
    primer = """
    You are an expert in the solar system. A highly intelligent system that answers user questions based on information provided by the user above each question.
    If the information cannot be found in the information provided by the user, you truthfully say:
    "I don't know".
    """  # System prompt for GPT-3
    llm_model = 'gpt-3.5-turbo'  # GPT-3 model for text generation
    user_prompt, ref = generate_augmented_query(query, embed_model=embed_model)  # Generate user prompt and reference
    system_prompt = primer  # Set system prompt
    return ask_gpt(system_prompt, user_prompt, model=llm_model), user_prompt, ref  # Return generated response, user prompt, and reference
