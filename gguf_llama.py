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

    def __init__(self, model_gguf_path:str, max_tokens:int, max_input_tokens:int, **llama_kwrgs) -> None:
        """
        Initialize the LlamaAI instance.

        Args:
            model_gguf_path (str): Path to .gguf model file.
            max_tokens (int): Max tokens to generate.
            max_input_tokens (int): Max tokens allowed in input.
            llama_kwrgs: Additional kwargs for Llama model.

        """
        self.model_path = model_gguf_path
        self.max_tokens = max_tokens
        self.max_input_tokens = max_input_tokens
        self.llm = None
        self.tokenizer = None
        self._loaded = False
        self.load()
        self._llama_kwrgs = llama_kwrgs
        
    def load(self) -> None:
        """
        Load the Llama model and tokenizer based on initialized attributes.

        Sets the llm and tokenizer attributes.
        Sets _loaded to True once complete.
        """
        print(f"Loading model from {self.model_path}...")
        self.llm = Llama(model_path=self.model_path, verbose=False, n_ctx=self.max_tokens, **self._llama_kwrgs)
        self.tokenizer = LlamaTokenizer(self.llm)
        self._loaded = True

    def try_fixing_format(self, text: str, only_letters: bool = False, rem_list_formatting: bool = False) -> str:
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
        
    def _adjust_max_tokens(self, new_max_tokens: int) -> None:
        """
        Adjust the max_tokens attribute.

        Args:
            new_max_tokens (int): The new max tokens value.

        Sets _loaded to False to trigger reloading.
        """
        self.max_tokens = new_max_tokens
        self._loaded = False
   
    def _adjust_max_input_tokens(self, new_max_input_tokens: int) -> None:
        """
        Adjust the max_input_tokens attribute.

        Args:
            new_max_input_tokens (int): The new max input tokens value.
        
        Raises an exception if the new value is less than max_tokens.
        """
        if new_max_input_tokens < self.max_tokens:
            raise Exception("The new maximum input tokens must be greater than the current maximum tokens.")
        self.max_input_tokens = new_max_input_tokens

    def adjust_tokens(self, new_max_tokens: int, new_max_input_tokens: int) -> None:
        """
        Adjust both the max tokens and max input tokens.

        Args:
            new_max_tokens (int): New max tokens value.
            new_max_input_tokens (int): New max input tokens value.

        Calls _adjust methods to update attributes.
        Reloads the model after adjusting.
        """
        self._adjust_max_tokens(new_max_tokens)
        self._adjust_max_input_tokens(new_max_input_tokens)
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

    def is_within_input_limit(self, text: str) -> bool:
        """
        Check if the text is within the max input tokens limit.

        Args:
            text (str): The text to check.

        Returns: 
            bool: True if under input token limit, False otherwise.
        """
        return self.count_tokens(text) <= self.max_input_tokens
    
    def infer(self,text:str, only_string: bool = False, max_tokens_if_needed=-1, stop_at_str=None, include_stop_str=True) -> str:
        """
        Generate inference text for the input prompt.

        Args:
            text (str): The prompt text.
            only_string (bool): Whether to return just text or OpenAI object. 
            max_tokens_if_needed (int): Tokens to try if text too long.
            stop_at_str (str): String to stop generation at.
            include_stop_str (bool): Whether to include stop string.

        Returns:
            str/list: The generated text or OpenAI inference object.

        Raises an exception if the text is too long and no max tokens provided.
        Adjusts model tokens if needed to fit prompt.
        """
        text = str(text)
        self._check_loaded()
        adjusted = False
        if not self.is_within_input_limit(text):
            if not max_tokens_if_needed or max_tokens_if_needed < 0:
                raise Exception("Text is too long!")
            else:
                print("Text is too long. Adjusting model trying to fit it...")
                current_max_tokens = self.max_tokens
                current_max_input_tokens = self.max_input_tokens
                input_to_total_ratio = current_max_input_tokens / current_max_tokens

                desired_prompt_len = self.count_tokens(text)
                if not any([max_tokens_if_needed > 0, desired_prompt_len - current_max_input_tokens <= max_tokens_if_needed]):
                    raise Exception("Text is too long and the model cannot be adjusted to fit it!")
                desired_input_len = int(desired_prompt_len * input_to_total_ratio)
                print(f"Adjusting model to {desired_input_len} input tokens and {desired_prompt_len} tokens.")
                self.adjust_tokens(desired_input_len, desired_prompt_len)
                adjusted = True
                
        stop_at = None if any([stop_at_str is None, stop_at_str == ""]) else stop_at_str
        output = self.llm(text, max_tokens=self.max_tokens, stop=stop_at)
        if only_string:
            output = self._text_from_inference_obj(output)
            if include_stop_str:
                output += stop_at_str if stop_at_str is not None else ""
        if adjusted:
            print(f"Adjusting model back to {current_max_tokens} tokens and {current_max_input_tokens} input tokens.")
            self.adjust_tokens(current_max_tokens, current_max_input_tokens)
        return output
    
    def _text_from_inference_obj(self, answer_dict: dict) -> str:
        if 'choices' in answer_dict and 'text' in answer_dict['choices'][0]:
            extracted_answ = answer_dict['choices'][0]['text']
        return extracted_answ