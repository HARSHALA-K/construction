from groq import Groq
from backend.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

models = client.models.list()

for model in models.data:
    print(model.id)