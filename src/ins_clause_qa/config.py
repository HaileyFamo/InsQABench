import os
import google.generativeai as genai
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


api_key = os.environ.get(['OPENAI_KEY'])

genai.configure(api_key=api_key, transport='rest')
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        logger.info("Available model:", m.name)



safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]


text_model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)
