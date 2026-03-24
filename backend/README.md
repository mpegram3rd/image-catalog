# Getting Started
The backend is managed with `uv` so you should [have that installed](https://docs.astral.sh/uv/getting-started/installation/).

While in the `backend` directory, run `uv sync` to create your `Virtual Environment` and
pull all the dependencies.

## Model Selection
You can use any Open AI API compatible model inference/embedding provider. 
This means you can use local models running on [Ollama](https://ollama.com/), and [LM Studio](https://lmstudio.ai/) just as easily
as you could models from [Gemini](https://gemini.google.com/) and [Open AI](https://openai.com/).

There are 2 primary model types required to run this application:
- Text Embedding: This is separately configurable and is used for storing descriptions and querying the generated descriptions
- LLM model for Description Generation and for Chatting with the catalog.
    - A `Vision` enabled model is required for the Description Generation during Indexing
    - `Tool Calling` is required for MCP integration but is not required for the Indexer

Multimodal Embedding is handled by the OpenCLIP model on Huggingface.  It is 
recommended but I don't believe required that you setup an account on Huggingface
and generate an API token which will be used in the [Configuration](#configuration)
section below.

### Some model suggestions to try out:
***For Inference***:
- (Small) `Gemma 3n (google/gemma-3n-e4b`
  - Fast and lightweight. 
- (Medium) `Qwen 3 VL 4B (qwen/qwen3-vl-4b)`
  - Slower but had fewer guardrails
  - Has `Tool` support (can be used with the MCP server)
- (Large) `Gemma 3 12B (google/gemma-3-12b)`
  - Larger memory footprint
  - Provided the most detailed descriptions of the images

***For Embedding***:
`Qwen 3` has several different sized text embedding models (0.6B / 4B)
that you can use for embedding the text descriptions during Indexing.

## Configuration
Create a `.env` file based off the provided `.env-local-example` file.

A few hints for how to do this with local model providers:
- For [Ollama](https://ollama.com/):
  - `LLM_PROVIDER='Ollama'`
  - `LLM_URL='http://localhost:11434/v1'`
  - `LLM_API_KEY='ANYTHING-YOU_WANT'`

- For [LM Studio](https://lmstudio.ai/):
  - `LLM_PROVIDER='LM Studio'`
  - `LLM_URL='http://localhost:1234/v1'`
  - `LLM_API_KEY='ANYTHING-YOU_WANT'`

## Execution
There are 2 applications for the backend.

### Indexer
The Indexer is responsible for processing the images and sub-folders starting from
the base folder defined in the `PHOTOS_BASE_PATH` 

To run the indexer: `uv run indexer.py`

Depending on the horsepower of your machine and the number of images this could take awhile,
but it logs out a lot of information about where it is in the process and how long each 
step of the image processing is taking so you can get an idea on performance and make
some decisions about what `Vision` enabled model works best for you.

### Server
The server provides both REST API and MCP endpoints.  The `React` frontend
uses the REST API, while the MCP Endpoints can be easily configured to use with 
your MCP provider. 

To run the server: `uv run server.py`

#### MCP Configuration
Here is a sample LM Studio MCP configuration for the Image Catalog features:
```json
{
  "mcpServers": {
    "image-catalog": {
      "url": "http://localhost:8000/ai/mcp"
    }
  }
}
```
