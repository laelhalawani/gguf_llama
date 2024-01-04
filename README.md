# gguf_llama

Provides a LlamaAI class with Python interface for generating text using Llama models.

## Features

- Load Llama models and tokenizers automatically from gguf file
- Generate text completions for prompts
- Automatically adjust model size to fit longer prompts up to a specific limit
- Convenient methods for tokenizing and untokenizing text  
- Fix text formatting issues before generating

## Usage

```python
from llama_ai import LlamaAI

ai = LlamaAI("my_model.gguf", max_tokens=500, max_input_tokens=100)"
```
Generate text by calling infer():
```python
text = ai.infer("Once upon a time")  
print(text)"
```
Adjust model tokens to fit longer prompts:
```python
"big_prompt = "..." # prompt longer than max input tokens   

text = ai.infer(big_prompt, max_tokens_if_needed=2000)"
```
## Installation

```python
pip install gguf_llama
``` 

## Documentation

See the [API documentation](https://laelhalawani.github.io/gguf_llama) for full details on classes and methods. 

## Contributing

Contributions are welcome! Open an issue or PR to improve gguf_llama.
