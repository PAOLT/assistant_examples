from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import json
import time
from IPython.display import clear_output
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
 

 
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:
        # print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        print("\n".join(citations))


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
    with client.beta.threads.runs.stream(thread_id=thread.id, assistant_id=assistant_id, instructions=question, event_handler=EventHandler()) as stream:
        stream.until_done()

    question = input("question: ")


