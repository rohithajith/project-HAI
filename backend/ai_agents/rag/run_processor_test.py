from transformers import AutoModelForCausalLM, AutoTokenizer

def get_model_info(model_name: str):
    try:
        model_path = r"C:\Users\2312205\Downloads\project-HAI\finetunedmodel-merged"
        print(f"Loading model from path: {model_path}")

        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path)

        return {
            "name": model_name,
            "is_loaded": True,
            "path": model_path,
            "tokenizer": tokenizer,
            "model": model
        }

    except Exception as e:
        return {
            "name": model_name,
            "is_loaded": False,
            "error": f"Error loading model {model_name}: {str(e)}"
        }