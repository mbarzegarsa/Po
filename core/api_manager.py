import aiohttp
import asyncio
import re
from typing import Tuple, List, Dict

class APIManager:
    BASE_URLS = {
        "openrouter": "https://openrouter.ai/api/v1/",
        "gemini": "https://generativelanguage.googleapis.com/v1beta/"
    }
    MODELS = {
        "openrouter": [
            ("DeepSeek V3", "deepseek/deepseek-v3:free"),
            ("Llama 3.3 70B Instruct", "meta-llama/llama-3.3-70b-instruct:free"),
            ("Qwen2.5 72B Instruct", "qwen/qwen-2.5-72b-instruct:free"),
        ],
        "gemini": [
            ("Gemini 2.0 Flash Experimental", "gemini-2.0-flash-exp"),
            ("Gemini 1.5 Flash-002", "gemini-1.5-flash-002"),
        ]
    }

    def __init__(self, service: str, api_key: str, use_proxy: bool = False):
        self.service = service.lower()
        self.api_key = api_key.strip()
        self.proxies = {"https": "https://middleman.yebekhe.workers.dev"} if use_proxy else None
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://myapp.example.com",
            "X-Title": "TranslatorApp"
        }

    async def validate_api_key(self) -> Tuple[bool, str]:
        async with aiohttp.ClientSession() as session:
            url = f"{self.BASE_URLS[self.service]}{'health' if self.service == 'openrouter' else f'models?key={self.api_key}'}"
            try:
                async with session.get(url, headers=self.headers if self.service == "openrouter" else {}, proxy=self.proxies["https"] if self.proxies else None, timeout=10) as response:
                    response.raise_for_status()
                    return True, "API key valid"
            except aiohttp.ClientError as e:
                return False, f"Invalid API key: {str(e)}"

    async def translate_text(self, text: str, target_lang: str, model: str, context: str = "", temperature: float = 0.7, top_p: float = 0.95, top_k: int = 40, max_output_tokens: int = 2048) -> str:
        if not text.strip() or len(text.strip()) < 3:
            return text
        if target_lang not in ["en", "fa", "ar"]:
            return text

        lang_map = {"en": "English", "fa": "Persian", "ar": "Arabic"}
        prompt = (
            f"Translate the text into {lang_map[target_lang]} for a WordPress plugin UI:\n"
            f"1. Return only the translated string.\n"
            f"2. Preserve placeholders (e.g., %s, %d, {{0}}, <tag>, [shortcode]).\n"
            f"3. Use standard WordPress UI terms.\n"
            f"4. Ensure concise, natural translations.\n"
            f"Context: {context or 'WordPress plugin UI'}\nInput: {text}"
        )

        async with aiohttp.ClientSession() as session:
            if self.service == "openrouter":
                url = f"{self.BASE_URLS['openrouter']}chat/completions"
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_output_tokens
                }
                headers = self.headers
            else:
                url = f"{self.BASE_URLS['gemini']}models/{model}:generateContent?key={self.api_key}"
                data = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": temperature, "topP": top_p, "maxOutputTokens": max_output_tokens}
                }
                headers = {"Content-Type": "application/json"}

            try:
                async with session.post(url, json=data, headers=headers, proxy=self.proxies["https"] if self.proxies else None, timeout=20) as response:
                    response.raise_for_status()
                    response_json = await response.json()
                    translated = response_json["choices"][0]["message"]["content"].strip() if self.service == "openrouter" else response_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                    return self._validate_response(text, translated)
            except aiohttp.ClientError:
                return text

    def _validate_response(self, original: str, translated: str) -> str:
        placeholder_pattern = r'%[sd]|%[0-9]\$[sd]|\{[0-9]+\}|\{[^{}]*?\}|\<[^>]+?\>|\[[^\]]+?\]'
        original_placeholders = re.findall(placeholder_pattern, original)
        translated_placeholders = re.findall(placeholder_pattern, translated)
        return translated if sorted(original_placeholders) == sorted(translated_placeholders) else original