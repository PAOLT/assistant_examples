from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import json

# parse script arguments from config file
with open("./assistant_def.json") as f:
  assistant_def = json.load(f)

sys_msg = assistant_def['sys_msg']
assistant_name = assistant_def['assistant_name'] 

# file_paths = ["Users/paolt/assistant_examples/Woodgrove Asset Management  - Prospective of Asset Management Funds.pdf"]
file_paths = []
for file_name in assistant_def["file_names"]:
  file_path = os.path.join(assistant_def['files_dir'], file_name['file_name'])
  file_paths.append(file_path)

chunking_strategy = {"type": assistant_def['chunking_strategy']['chunking_strategy_type'], #"static" # can be 'auto' and 'static' 
                     "static": {"max_chunk_size_tokens": assistant_def['chunking_strategy']['max_chunk_size'], #1024  
                                "chunk_overlap_tokens": assistant_def['chunking_strategy']['overlap_size'], #50
                                }
                    } 

max_num_results = assistant_def['max_num_results'] # 5

ranking_options = {"ranker": assistant_def['ranker']['ranker'], # can be 'auto' and 'default...'
                   "score_threshold": assistant_def['ranker']['score_threshold']}

# connect to Az OAI

load_dotenv()

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
