from typing import Any, Optional, Union
from llama_cpp import Llama, LlamaTokenizer
from util_helper.text_preprocessor import remove_list_formatting, remove_non_letters

class LlamaAI:
    """
    A class for interfacing with Llama models.

    Attributes:
        model_path (str): The path to the Llama model file.
        max_tokens (int): The maximum number of tokens to generate.
        max_input_tokens (int): The maximum number of tokens allowed in the input text.
        llm (Llama): The loaded Llama model instance. 
        tokenizer (LlamaTokenizer): The tokenizer for encoding/decoding text.
        _loaded (bool): Whether the model is loaded.
        _llama_kwrgs (dict): Additional kwargs to pass when loading Llama model.
    """

    def __init__(self, model_gguf_path:str, max_tokens:int, **llama_kwargs:Any) -> None:
        """
        Initialize the LlamaAI instance.

        Args:
            model_gguf_path (str): Path to .gguf model file.
            max_tokens (int): Max tokens to be processed 
            llama_kwrgs: Additional kwargs for Llama model compatible with llama-cpp-python BE

        """
        self.model_path = model_gguf_path
        self.max_tokens = max_tokens
        self._max_input_tokens = None
        self.llm = None
        self.tokenizer = None
        self._loaded = False
        self._llama_kwrgs = llama_kwargs
        self._embeddings_mode = True
        self.load()

        
    def load(self) -> None:
        """
        Load the Llama model and tokenizer based on initialized attributes.

        Sets the llm and tokenizer attributes.
        Sets _loaded to True once complete.
        """
        print(f"Loading model from {self.model_path}...")
        llama_kwargs = {"embedding": self._embeddings_mode}
        for k, v in self._llama_kwrgs.items():
            llama_kwargs[k] = v
        self.llm = Llama(model_path=self.model_path, verbose=False, n_ctx=self.max_tokens, **llama_kwargs)
        self.tokenizer = LlamaTokenizer(self.llm)
        self._loaded = True

    def create_embeddings(self, text:str) -> list[float]:
        """
        Create embeddings for the input text.

        Args:
            text (str): The text to create embeddings for.
        """
        self._check_loaded()
        if not self._embeddings_mode:
            print("Switching to embeddings mode...")
            self._embeddings_mode = True
            self.load()
        embs = self.llm.embed(text)
        return embs

    def _try_fixing_format(self, text: str, only_letters: bool = False, rem_list_formatting: bool = False) -> str:
        """
        Attempt to fix formatting issues in the input text.

        Removes extra newlines, non-letter characters, and list formatting.
        Prints a message if changes are made.

        Args:
            text (str): The input text to fix.
            only_letters (bool): Whether to remove all non-letters.
            rem_list_formatting (bool): Whether to remove list formatting.

        Returns:
            str: The fixed text.
        """
        print("Trying to fix formatting... this might have some undersired effects")
        changes = False
        if "\n\n" in text:
            #split text in that place
            core_info = text.split("\n\n")[1:]
            text = " ".join(core_info)
            changes = True
        if "\n" in text:
            text = text.replace("\n", " ")
            changes = True
        if only_letters:
            text = remove_non_letters(text)
            changes = True
        if rem_list_formatting:
            text = remove_list_formatting(text)
        if changes:
            print("The text has been sucessfully modified.")
        return text

    def _check_loaded(self) -> None:
        """
        Check if the model is loaded, load it if not.

        Raises an exception if loading fails.
        """
        if not self._loaded:
            try:
                self.load()
                raise Warning("Model not loaded, trying a default reload...")
            except:
                raise Exception("Model not loaded! Please provide model settings when creating the class or use load_model method after creation.")
        
    def _set_total_token_limit(self, new_max_tokens: int) -> None:
        """
        Adjust the max_tokens attribute.

        Args:
            new_max_tokens (int): The new max tokens value.

        Sets _loaded to False to trigger reloading.
        """
        self.max_tokens = new_max_tokens
        self._loaded = False
   
    def _set_input_token_limit(self, new_max_input_tokens: int=None) -> None:
        """
        Adjust the max_input_tokens attribute.

        Args:
            new_max_input_tokens (int): The new max input tokens value.
        
        Raises an exception if the new value is less than max_tokens.
        """
        if new_max_input_tokens is None or (new_max_input_tokens is not None and new_max_input_tokens <= 0):
            self._max_input_tokens = None
            print("Max input tokens limit cleared.")
        elif new_max_input_tokens < self.max_tokens:
            raise Exception("The new maximum input tokens must be greater than the current maximum tokens.")
        elif self._max_input_tokens is None or new_max_input_tokens != self._max_input_tokens:
            self._max_input_tokens = new_max_input_tokens

    def set_max_tokens(self, new_max_tokens: int, max_input_tokens_limit:Optional[int]=None) -> None:
        """
        Adjust both the max tokens and max input tokens.

        Args:
            new_max_tokens (int): New max tokens value.
            new_max_input_tokens (int): New max input tokens value.

        Calls _adjust methods to update attributes.
        Reloads the model after adjusting.
        """
        self._set_total_token_limit(new_max_tokens)
        self._set_input_token_limit(max_input_tokens_limit)
        self.load()

    def tokenize(self, text: str) -> list:
        """
        Tokenize the input text using the loaded tokenizer.

        Args:
            text (str): The text to tokenize.
        
        Returns:
            list: The list of tokenized tokens.
        """
        ts = self.tokenizer.encode(text)
        return ts
    
    def untokenize(self, tokens: list) -> str:
        """
        Decode a list of tokens back into a string.

        Args:
            tokens (list): The tokens to untokenize.

        Returns:
            str: The decoded string.
        """
        return self.tokenizer.decode(tokens)
            
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens needed to tokenize the text.

        Args:
            text (str): The text to count tokens for.

        Returns:
            int: The number of tokens.
        """
        return len(self.tokenize(text))    

    def is_prompt_within_limit(self, text: str) -> bool:
        """
        Check if the text is within the max input tokens limit.

        Args:
            text (str): The text to check.

        Returns: 
            bool: True if under input token limit, False otherwise.
        """
        tcc = self.count_tokens(text)
        print(f"Input length: {tcc} tokens")
        if self._max_input_tokens is not None:
            r = self.count_tokens(text) <= self.max_tokens
            print(f"Max input length set to: {self._max_input_tokens} tokens")
        else:
            r = self.count_tokens(text) <= self.max_tokens
            print(f"Max input length not set, using max tokens: {self.max_tokens} tokens")
        return r

    def clear_input_tokens_limit(self) -> None:
        """
        Clear the max input tokens limit.
        """
        self._set_input_token_limit(None)
    
    def infer(self, text:str, only_string: bool = True, stop_at_str=None, include_stop_str=True) -> Union[str, dict]:
        """
        Generate inference text for the input prompt.

        Args:
            text (str): The prompt text.
            only_string (bool): Whether to return just text or OpenAI object. 
            stop_at_str (str): The string to stop at.
            include_stop_str (bool): Whether to include the stop string in the output.

        Returns:
            str/list: The generated text or OpenAI inference object.

        Raises an exception if the text is too long and no max tokens provided.
        Adjusts model tokens if needed to fit prompt.
        """
        text = str(text)
        self._check_loaded()
        if not self.is_prompt_within_limit(text):
            raise Exception("Text is too long!")
        else:            
            stop_at = None if any([stop_at_str is None, stop_at_str == ""]) else stop_at_str
            output:dict = self.llm(text, max_tokens=self.max_tokens, stop=stop_at)
            if only_string:
                output = self._text_from_inference_obj(output)
                if include_stop_str:
                    output += stop_at_str if stop_at_str is not None else ""
            return output
    
    def _text_from_inference_obj(self, answer_dict: dict) -> str:
        if 'choices' in answer_dict and 'text' in answer_dict['choices'][0]:
            extracted_answ = answer_dict['choices'][0]['text']
        return extracted_answ