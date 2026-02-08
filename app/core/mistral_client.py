from mistralai import Mistral
from app.core.config import MISTRAL_API_KEY

def get_mistral_client() -> Mistral:
    return Mistral(api_key=MISTRAL_API_KEY)
