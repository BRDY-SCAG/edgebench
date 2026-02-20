"""
backends/ollama_backend.py
Wraps Ollama's local API for inference + timing.
"""

import time
import requests


# The standard prompts we run for every benchmark
# Keeping them short and deterministic so results are comparable
BENCHMARK_PROMPTS = [
    {
        "id": "short_factual",
        "prompt": "What is the capital of France? Answer in one sentence.",
        "category": "factual"
    },
    {
        "id": "short_reasoning",
        "prompt": "If a train travels 60 miles per hour for 2 hours, how far does it travel? Show your work briefly.",
        "category": "reasoning"
    },
    {
        "id": "short_creative",
        "prompt": "Write a single sentence describing a sunset over the ocean.",
        "category": "creative"
    }
]


class OllamaBackend:
    def __init__(self, model: str, host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.name = "ollama"

    def is_available(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=3)
            if response.status_code != 200:
                return False
            models = [m["name"] for m in response.json().get("models", [])]
            # Check if our model is available (handle tags like llama3.2:3b)
            return any(self.model in m for m in models)
        except requests.exceptions.ConnectionError:
            return False

    def infer(self, prompt: str) -> dict:
        """
        Send a prompt to Ollama and return timing + response data.
        Uses the /api/generate endpoint with stream=False for simplicity.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,       # deterministic output
                "seed": 42,             # reproducible
                "num_predict": 128,     # cap response length for fairness
            }
        }

        start_time = time.perf_counter()

        response = requests.post(
            f"{self.host}/api/generate",
            json=payload,
            timeout=120
        )
        response.raise_for_status()

        end_time = time.perf_counter()
        data = response.json()

        total_time_ms = (end_time - start_time) * 1000

        # Ollama gives us eval_count (tokens generated) and eval_duration (ns)
        eval_count = data.get("eval_count", 0)
        eval_duration_ns = data.get("eval_duration", 1)
        prompt_eval_count = data.get("prompt_eval_count", 0)
        prompt_eval_duration_ns = data.get("prompt_eval_duration", 1)

        tokens_per_second = (eval_count / eval_duration_ns) * 1e9 if eval_count else 0
        prompt_tokens_per_second = (prompt_eval_count / prompt_eval_duration_ns) * 1e9 if prompt_eval_count else 0

        return {
            "response": data.get("response", ""),
            "total_time_ms": round(total_time_ms, 2),
            "tokens_generated": eval_count,
            "tokens_per_second": round(tokens_per_second, 2),
            "prompt_tokens": prompt_eval_count,
            "prompt_tokens_per_second": round(prompt_tokens_per_second, 2),
            "time_to_first_token_ms": round((prompt_eval_duration_ns / 1e6), 2),
        }

    def get_prompts(self) -> list:
        return BENCHMARK_PROMPTS
