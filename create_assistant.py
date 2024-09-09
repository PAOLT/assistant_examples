from openai import AzureOpenAI
from dotenv import load_dotenv
import os
# import json
# import time
# from IPython.display import clear_output

# script arguments
sys_msg='''You are a financial assistant who answer customer questions to help them understanding the details about Woodgrove management funds. 
You are upbeat and friendly. If the customer greets you, you greet them back. 
You provide succint and short answers to customer questions, by sharing no more than 3 bullet points. 
Only use the provided context. If the context is not useful, do not use your own knowledge to make up answers. 
Instead, state that you are an assistant for Woodgrove Financial products only and to consider rephrasing the question.'''
assistant_name = "Financial Analyst Assistant"

# vectore store arguments
# check: https://platform.openai.com/docs/api-reference/assistants/createAssistant?lang=python

file_paths = ["Users/paolt/assistant_examples/Woodgrove Asset Management  - Prospective of Asset Management Funds.pdf"]

chunking_strategy_type = "static" # can be 'auto' and 'static'
max_chunk_size = 1024
overlap_size = 50
chunking_strategy = {"type": chunking_strategy_type, "static": {"max_chunk_size_tokens": max_chunk_size,  "chunk_overlap_tokens": overlap_size}}
# chunking_strategy = {"type": chunking_strategy_type, "parameters": {"max_chunk_size": max_chunk_size,  "overlap_size": overlap_size}}

max_num_results = 5

ranker = "auto" # can be 'auto' and 'default...'
score_threshold = 0.7
ranking_options = {"ranker": ranker, "score_threshold": score_threshold}

# load configuration parameters into environment variables
load_dotenv()

# connect to Az OAI
try:
  client = AzureOpenAI(
      api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
      api_version="2024-05-01-preview",
      azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
      )
except Exception as e:
  print("Failed to connect to the assistant")
  raise e  

# Create an assistant
try:
  print(f"Creating assistant {assistant_name}...", end=' ')
  assistant = client.beta.assistants.create(
    name=assistant_name,
    instructions=sys_msg,
    model=os.getenv("AZURE_OPENAI_MODEL"),
    tools=[{"type": "file_search", "file_search": {"max_num_results": max_num_results}}], #, "ranking_options": ranking_options
  )
  print("OK")
except Exception as e:
  print(f"FAILED!")
  raise e

# Create a vector store 
try:
  print(f"Creating a vector store...", end=' ')
  vector_store = client.beta.vector_stores.create(name="Woodgroove vector store")
  file_streams = [open(path, "rb") for path in file_paths]
  
  # Use the upload and poll SDK helper to upload the files, add them to the vector store, and poll the status of the file batch for completion.
  file_batch = client.beta.vector_stores.file_batches.upload_and_poll(vector_store_id=vector_store.id, files=file_streams, chunking_strategy=chunking_strategy)
  print(f"{file_batch.status}; {file_batch.file_counts}")
except Exception as e:
  print("FAILED!")
  raise e

try:
  assistant = client.beta.assistants.update(assistant_id=assistant.id,tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}})
  print(f"The following assistant have been created with {file_batch.file_counts.completed} files:")
  print(assistant.id)
except Exception as e:
  print("Failed to finalize the assistant creation")
  raise e
