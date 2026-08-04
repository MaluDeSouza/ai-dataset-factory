import os
import logging
import google.generativeai as genai
from openai import OpenAI


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider:
    def __init__(self):
        self.active_providers = []
        
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.active_providers.append("gemini")
            
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
            self.active_providers.append("openai")

        if not self.active_providers:
            raise ValueError("Nenhuma chave de API encontrada. Defina GEMINI_API_KEY ou OPENAI_API_KEY no .env")

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
        """
        Tenta gerar o texto passando por todos os provedores ativos.
        Se um falhar, pula para o próximo automaticamente.
        """
        for provider in self.active_providers:
            try:
                if provider == "gemini":
                    return self._call_gemini(system_prompt, user_prompt, temperature)
                elif provider == "openai":
                    return self._call_openai(system_prompt, user_prompt, temperature)
            except Exception as e:
                logger.warning(f"Provedor '{provider}' falhou: {str(e)}. Tentando o próximo...")
                continue
        
        
        raise RuntimeError("Todos os provedores de LLM falharam ou estão indisponíveis no momento.")

    def _call_gemini(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash", 
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(temperature=temperature)
        )
        response = model.generate_content(user_prompt)
        return response.text.strip()

    def _call_openai(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content.strip()