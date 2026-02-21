"""
    backend/mlx_backend.py
    
    officially entering my script kitty era 

    wrap mlx-lm for native apple silicon inference + timing
    onlyt works for apple silicon M1+

    Install pip install mlx-lm
    models on huggingface/mlx-community


"""

import time 
import platform
from backends.ollama_backend import BENCHMARK_PROMPTS


class MLXBackend:
    def __init__(self, model: str = "mlx-community/Llama-3.2-4B-Instruct-4bit"):
        self.model = model
        self.name = "mlx"
        self._model = None
        self._tokenizer = None

    def is_available(self) -> bool:
        """"check to see if were on apple silicon and mlx-lm is installed"""

        if platform.system() != "Darwin": 
            print(f"    MLX is only supported on macOS")
            return False
        if platform.machine() != "arm64":
            print(f"     MLX requires Apple Silicon idiot")
            return False
        try:
            import mlx_lm
            return True
        except ImportError:
            print("you don't have mlx-lm installed idiot: Run pip install mlx-lm")
            return False

    def load_model(self):
            """lazy load our model only happens on first inference call"""
            if self._model is None:
                from mlx_lm import load
                print(f"    Loading model {self.model} into MLX ...")
                print(f" (this may take a few minutes lmao)\n")
                result = load(self.model)
                if isinstance(result, tuple):
                    self._model, self._tokenizer = result[0], result[1]

    def infer(self, prompt: str) -> dict: 
        """run inference with mlx-lm and return timing + response data.
            mlx doesn't give us TTFT directly so we have to measure that shit ourselves
        """

        from mlx_lm import stream_generate

        self.load_model()

        assert self._model is not None, "Model failed to load"
        assert self._tokenizer is not None, "Tokenizer failed to load"

        tokenizer = self._tokenizer

        if tokenizer is not None and hasattr(tokenizer, "apply_chat_template"):
            messages = [{"role": "user", "content": prompt}]
            formatted_prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            formatted_prompt = prompt

        tokens_generated = 0
        first_token_time = 0
        full_response = []
        last_response = None
        first_response = None
        start_time = time.perf_counter()

        for response in stream_generate(
            self._model,
            tokenizer,
            prompt=formatted_prompt,
            max_tokens = 128,
        ):
            if first_token_time is None:
                first_token_time = time.perf_counter()
            full_response.append(response.text)
            tokens_generated += 1
            last_response = response

        end_time = time.perf_counter()

        total_time_ms = (end_time - start_time) * 1000

        if last_response and last_response.prompt_tps > 0:
            ttft_ms = (last_response.prompt_tokens / last_response.prompt_tps) * 1000
        else:
            ttft_ms = 0

        generation_tps = last_response.generation_tps if last_response else 0
        prompt_tps = last_response.prompt_tps if last_response else 0
        prompt_tokens = last_response.prompt_tokens if last_response else 0


        return {
            "response": "".join(full_response),
            "total_time_ms": round(total_time_ms, 2),
            "tokens_generated": tokens_generated,
            "tokens_per_second": round(generation_tps, 2),
            "prompt_tokens": prompt_tokens,
            "prompt_tokens_per_second": round(prompt_tps, 2),
            "time_to_first_token_ms": round(ttft_ms, 2),
        }

    def get_prompts(self) -> list:
        return BENCHMARK_PROMPTS



