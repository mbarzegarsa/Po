from typing import List, Tuple

class APIModels:
    MODELS = {
        "openrouter": [
            ("DeepSeek V3", "deepseek/deepseek-v3:free"),
            ("Llama 3.3 70B Instruct", "meta-llama/llama-3.3-70b-instruct:free"),
            ("Qwen2.5 72B Instruct", "qwen/qwen-2.5-72b-instruct:free"),
            ("Mistral 7B Instruct", "mistralai/mistral-7b-instruct:free"),
            ("Llama 3.1 405B", "meta-llama/llama-3.1-405b:free"),
        ],
        "gemini": [
            ("Gemini 2.0 Flash Experimental", "gemini-2.0-flash-exp"),
            ("Gemini 1.5 Flash-002", "gemini-1.5-flash-002"),
            ("Gemini 1.5 Pro-002", "gemini-1.5-pro-002"),
        ]
    }

    @staticmethod
    def get_models(service: str) -> List[Tuple[str, str]]:
        return APIModels.MODELS.get(service.lower(), [])