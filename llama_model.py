from gpt4all import GPT4All

# ✔️ Tumhara actual model folder path
MODEL_PATH = "C:/Users/maazf/AppData/Local/nomic.ai/GPT4All"

# ✔️ Correct model name from your system
MODEL_NAME = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"

# ✅ Don't let it try to download — use only local
model = GPT4All(MODEL_NAME, model_path=MODEL_PATH, allow_download=False)

def get_response(prompt):
    response = model.chat_completion(prompt)
    return response
