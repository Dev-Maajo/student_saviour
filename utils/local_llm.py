# utils/local_llm.py

from gpt4all import GPT4All
import time
import os

# ✅ Path to your GGUF model
model_path = "models/Meta-Llama-3-8B-Instruct.Q4_0.gguf"

# Check model existence
if not os.path.exists(model_path):
    raise FileNotFoundError(f"❌ Model file not found at path: {model_path}")

# 🔁 Load the model once at module level
try:
    model = GPT4All(model_path)
except Exception as e:
    raise RuntimeError(f"❌ Failed to load model: {str(e)}")

# === Function: General Prompt Completion ===
def get_completion(prompt):
    """
    Used for advanced generation tasks.
    """
    try:
        with model.chat_session():
            response = model.generate(
                prompt=prompt,
                max_tokens=150,
                temp=0.7,
                top_k=40,
                top_p=0.9,
                repeat_penalty=1.2
            )
        return response.strip()
    except Exception as e:
        print(f"❌ get_completion Error: {str(e)}")
        return f"❌ get_completion Error: {str(e)}"

# === Function: Simple LLM Prompt ===
def get_llm_response(prompt):
    """
    Main function used in app.py (career advice, suggestions, roadmap).
    Keeps things simple with reasonable defaults.
    """
    try:
        with model.chat_session():
            response = model.generate(
                prompt=prompt,
                max_tokens=300,
                temp=0.6
            )
        return response.strip()
    except Exception as e:
        print(f"❌ get_llm_response Error: {str(e)}")
        return f"❌ Error: {str(e)}"
