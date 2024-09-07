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

assistant_id = os.getenv("ASSISTANT")
thread = client.beta.threads.create()
question = input("question: ")

while question != 'goodbye':

    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=question)
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

    while run.status not in ["completed", "cancelled", "expired", "failed"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id,run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    data = json.loads(messages.model_dump_json(indent=2))
    answer = data['data'][0]['content'][0]['text']['value']
    print(f"answer: {answer}")

    question = input("question: ")

