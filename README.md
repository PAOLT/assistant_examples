# Assistant answering domain-specific user questions

This is an example of using the Azure OpenAI Assistant API to implement a basic chat bot, answering to domain-specific user questions based on some provided support files.
For details, see the product documentation here: https://platform.openai.com/docs/assistants/overview

## Running

- Create a Python environment using `requirements.txt`
- Create a `.env` file with Azure OpenAI end-point, key and model deployment (see `env_template` as an example)
- Configure your assistant by editing `assistant_def.json`
- Run `create_assistant.py` to create the assistant
- Copy the provided assistant ID (e.g., *asst_fnxjnyGTgMUDJUfzXt2GjJAL*) into your `.env` file
- Finally chat using `chat.py`. Some sample questions are provided in `sample_questions.txt`.


## Assistant configuration

- `sys_msg` is the prompt's system message given to the assistant
- The file_search tool is used: use `files_dir` and `file_names` to specify the files you want to use.
- The `chunking_strategy__type` can be *auto* and *static*. `max_chunk_size` and `overlap_size` refer to the size of chunks (ignored if *auto* is selected, and defaults to 800 and 400 respectively)
- `max_num_results` provides the number of top search results used by the assistant
- The ranker parameter `score_threshold` refers to the threshold used to consider search results as eligible

For vector store arguments check https://platform.openai.com/docs/api-reference/assistants/createAssistant?lang=python.

For assistant arguments check https://platform.openai.com/docs/api-reference/vector-stores?lang=python


## Limitations

- `chat.py` implements a synchronous chat session. OpenAI streaming and asynchronous processing are not used.
- Within the assistant configuration, the ranker parameters are not used.
- Scripts to manage artifacts are not provided. Consider that they might consume cloud resources, and using a tool like Azure AI Studio to manually delete unused files, vector stores and assistants (or your own script).
- The chat script is extremely basic, e.g., no roboust error handling and no reference visualization.
