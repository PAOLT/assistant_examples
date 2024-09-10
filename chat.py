from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import json

def parse_assistant_answer(thread):
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    data = json.loads(messages.model_dump_json(indent=2))
    answer = data['data'][0]['content'][0]['text']['value']
    return answer

# connect to OpenAI and create an empty thread
load_dotenv() 

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-05-01-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    max_retries=2, #default
    )

assistant_id = os.getenv("ASSISTANT")

thread = client.beta.threads.create()

# start chatting

question = input("question: ")
while question != 'bye':
    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=question)
    run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant_id)

    if run.status == "completed":        
        answer = parse_assistant_answer(thread)
        print(f"assistant > {answer}")
    else:
        print(f"assistant > sorry, something went wrong!")

    question = input("\nuser ('bye' to quit) > ")

