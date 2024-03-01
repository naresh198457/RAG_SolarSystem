import textwrap
import os
from openai import OpenAI
from pinecone import Pinecone


# Initializing the OpenAI
os.environ['OPENAI_API_KEY']='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' 
client=OpenAI()

# Initialize the pinecone vector database and call the database 
os.environ['PINECONE_API_KEY']='05ac17ba-3537-4e2e-a061-dc75ce2f948e'
# Setup the pinecone Environment
os.environ['PINECONE_ENVIRONMENT']='gcp-starter'

# initialize Connection to pinecone
api_key=os.getenv('PINECONE_API_KEY')
env=os.getenv('PINECONE_ENVIRONMENT')
pc=Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

# connect to existing Index:
index=pc.Index('my-solar-system')
index.describe_index_stats()

# Useful Functions
#-----------------------------------------------------------------------------
# Get the text embeddings. 
def get_embedding(text, model="text-embedding-ada-002"):
  text = text.replace("\n"," ")
  return client.embeddings.create(input=text, model=model).data[0].embedding

# retrieving the data from the Pinecone
def generate_augmented_query(query,embed_model='text-embedding-ada-002',k=5):
  # query from the user
  xq = get_embedding(query,model=embed_model)

  res = index.query(vector=xq, top_k=k,include_metadata=True)

  contexts =[item['metadata']['text'] for item in res['matches']]
  ref=[item['metadata']['ref'] for item in res['matches']]

  return "\n\n---\n\n".join(contexts)+"\n\n-----\n\n"+query, "\n---\n".join(ref)+"\n-----\n"+query

# sending system prompt and user prompt to the LLM. 
def ask_gpt(system_prompt, user_prompt,model='gpt-3.5-turbo'):

  temperature_=0.7 # Tunning parameter
  completion = client.chat.completions.create(model=model,
                                              temperature=temperature_,
                                              messages=[{'role':'system',
                                                         'content':system_prompt},
                                                        {'role':'user',
                                                         'content':user_prompt}])
  
  lines = (completion.choices[0].message.content).split("\n")
  lists = (textwrap.TextWrapper(width=90,break_long_words=False).wrap(line) for line in lines)

  return "\n".join("\n".join(list) for list in lists)

def rag_response(query):

    embed_model='text-embedding-ada-002'
    # System prompt is 
    primer=f"""
    You are a expert in solar system. A highly intelligent system that answer
    user question based on information provided by the user above each question.
    If the information cannot be found in the information provided by the use, you truthfully say:
    "I don't know".
    """

    llm_model='gpt-3.5-turbo' # LLM Model
    user_prompt, ref=generate_augmented_query(query,embed_model=embed_model)
    system_prompt=primer
    return ask_gpt(system_prompt,user_prompt,model=llm_model), user_prompt, ref
# ---------------------------------------------------------------------------------
