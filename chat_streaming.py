from openai import AzureOpenAI
from dotenv import load_dotenv
import os
from openai.types.beta.threads import Message, MessageDelta, Text, TextDelta
from typing_extensions import override
from openai import AssistantEventHandler
 

 
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)
    
    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
        if not delta.annotations:
            print(delta.value, end="", flush=True)
        # else:
        #     for annotation in delta.annotations:
        #         print(f"\n{annotation.text}: {annotation.type}", end="", flush=True)
    
    @override
    def on_text_done(self, text: Text) -> None:
        print(f"\nFULL TEXT\n{text.value}")   

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant is using a tool: {tool_call.type}\n", flush=True)


load_dotenv() 

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-05-01-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

assistant_id = os.getenv("ASSISTANT")
thread = client.beta.threads.create()


question = input("question: ")


while question not in ['goodbye','bye']:
    with client.beta.threads.runs.stream(thread_id=thread.id, assistant_id=assistant_id, instructions=question, event_handler=EventHandler()) as stream:
        stream.until_done()
    
    # with client.beta.threads.runs.stream(thread_id=thread.id, assistant_id=assistant_id, instructions=question) as stream:
    #     for text in stream.text_deltas:
    #         print(text, end="", flush=True)
    #     print()

    question = input("question: ")


