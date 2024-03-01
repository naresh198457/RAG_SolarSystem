# Importing necessary libraries and modules
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from openai import OpenAI  # Importing OpenAI library
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Importing text splitter from langchain
from pinecone import Pinecone  # Importing Pinecone library for vector indexing
import json, ast  # Importing JSON library for handling JSON data

# Initializing OpenAI
os.environ['OPENAI_API_KEY'] = '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'  # Setting OpenAI API key
client = OpenAI()  # Initializing OpenAI client

# Initializing Pinecone
os.environ['PINECONE_API_KEY'] = '05ac17ba-3537-4e2e-a061-dc75ce2f948e'  # Setting Pinecone API key

# Function to get embeddings from OpenAI
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")  # Replace newline characters with spaces
    return client.embeddings.create(input=text, model=model).data[0].embedding

# Function to generate unique IDs
def generate_ids(number, size):
    import string, random
    ids = []
    for i in range(number):
        res = ''.join(random.choices(string.ascii_letters, k=size))  # Generate random alphanumeric string
        ids.append(res)
        if len(set(ids)) != i + 1:  # Check if the generated ID is unique
            i = -1
            ids.pop(-1)
    return ids

# Function to load text chunks into a DataFrame
def load_chunks(df, split_text, REF):
    ids = generate_ids(len(split_text), 7)  # Generate unique IDs for chunks
    i = 0
    for chunk in split_text:
        ref = REF[i]  # Get the reference for the chunk
        df.loc[i] = [ids[i], get_embedding(chunk[0], model="text-embedding-ada-002"), {'text': chunk[0], 'ref': ref}]
        i += 1
    return df

# Function to split a sequence into chunks
def chunker(seq, size):
    for pos in range(0, len(seq), size):
        yield seq.iloc[pos:pos + size]

# Function to convert DataFrame to a list of tuples
def convert_data(chunk):
    data = []
    for i in chunk.to_dict('records'):
        data.append(i)
    return data

# Reading the Solar Data from an Excel file
Solar_Data = pd.read_excel(r"G:\My Drive\ITC_DS\Assignments\Week7_RAG\Topics\Solar_Data_V3.xlsx")
print(Solar_Data.shape)  # Print the shape of the DataFrame
print(Solar_Data.columns)  # Print the columns of the DataFrame

# Initializing a text splitter
my_text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100, length_function=len)

# Splitting the text into chunks using the text splitter
chunks = []
ref = Solar_Data['Source']
for i in range(len(Solar_Data)):
    chunks.append(my_text_splitter.split_text(Solar_Data.loc[i, 'Text']))

# Loading the chunks into a DataFrame and extracting embeddings
pre_upsert_df = pd.DataFrame(columns=['id', 'values', 'metadata'])
pre_upsert_df = load_chunks(pre_upsert_df, chunks, ref)

print(pre_upsert_df.loc[1, 'metadata']['ref'])  # Print reference for the second chunk

# Setting up the Pinecone environment and connecting to an existing index
os.environ['PINECONE_ENVIRONMENT'] = 'gcp-starter'  # Setting Pinecone environment
api_key = os.getenv('PINECONE_API_KEY')
env = os.getenv('PINECONE_ENVIRONMENT')
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))  # Initialize Pinecone client
index = pc.Index('my-solar-system')  # Connect to the existing index
print(index.describe_index_stats())  # Print index statistics

# Upserting vectors into the index
index_df = pre_upsert_df.copy()
print(index_df)
for chunk in chunker(index_df, 200):
    index.upsert(vectors=convert_data(chunk))  # Upsert vectors into the index
print(index.describe_index_stats)  # Print index statistics