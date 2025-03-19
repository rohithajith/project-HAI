import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download

def download_model():
    """Download the model from Hugging Face and save it locally"""
    model_id = "rohith0990/finetunedmodel-merged"
    local_dir = "./finetunedmodel-merged"
    
    print(f"Downloading model from: {model_id}")
    
    snapshot_download(repo_id=model_id, local_dir=local_dir)
    
    print("✅ Model downloaded successfully!")

if __name__ == "__main__":
    download_model()