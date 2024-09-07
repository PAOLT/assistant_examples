from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import json
import time
from IPython.display import clear_output

load_dotenv() # config = dotenv_values()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-05-01-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )


assistant = client.beta.assistants.create(
  name="Financial Analyst Assistant",
  instructions="You are an expert financial analyst. Use your knowledge base to answer questions about audited financial statements.",
  model=os.getenv("AZURE_OPENAI_MODEL"),
  tools=[{"type": "file_search"}],
)

# Create a vector store called "Financial Statements"
vector_store = client.beta.vector_stores.create(name="Financial Statements")
 
# Ready the files for upload to OpenAI
file_paths = ["/home/azureuser/cloudfiles/code/Users/paolt/okr_spike/bert_paper.pdf", "/home/azureuser/cloudfiles/code/Users/paolt/okr_spike/gpt_2_paper.pdf"]
file_streams = [open(path, "rb") for path in file_paths]
print("Indexing files")

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)
 
# You can print the status and the file counts of the batch to see the result of this operation.

# while file_batch.file_counts.in_progress>0:
#     time.sleep(3)

print(file_batch.status)
print(file_batch.file_counts)

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

print(f"The following assistant have been created with {file_batch.file_counts.completed} files:")
print(assistant.id)



