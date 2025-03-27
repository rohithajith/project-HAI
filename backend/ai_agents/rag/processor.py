from backend.ai_agents.models import get_model_info

class TextProcessor:
    model_info = get_model_info("finetuned_merged")

    if model_info["is_loaded"]:
        tokenizer = model_info["tokenizer"]
        model = model_info["model"]
    else:
        raise Exception(model_info["error"])

    @classmethod
    def _ask_model(cls, prompt: str, max_tokens: int = 256) -> str:
        inputs = cls.tokenizer(prompt, return_tensors="pt")
        outputs = cls.model.generate(**inputs, max_new_tokens=max_tokens)
        return cls.tokenizer.decode(outputs[0], skip_special_tokens=True)


    @classmethod
    def preprocess_query(cls, query: str) -> str:
        prompt = f"Clean and simplify this hotel-related query:\n'{query}'\nProcessed:"
        return cls._ask_model(prompt)

    @classmethod
    def expand_query(cls, query: str) -> list:
        prompt = f"Generate 3 related queries for hotel context:\n'{query}'\n-"
        output = cls._ask_model(prompt)
        return [line.strip("- ").strip() for line in output.split("\n") if line.strip()]

    @classmethod
    def extract_keywords(cls, text: str) -> list:
        prompt = f"Extract important keywords from this hotel-related text:\n{text}\nKeywords:"
        output = cls._ask_model(prompt)
        return [kw.strip() for kw in output.replace("Keywords:", "").split(",")]

    @classmethod
    def generate_query_variations(cls, query: str) -> list:
        prompt = f"Rephrase the query into 3 different variations:\n'{query}'\n-"
        output = cls._ask_model(prompt)
        return [line.strip("- ").strip() for line in output.split("\n") if line.strip()]

    @classmethod
    def extract_metadata(cls, text: str) -> dict:
        prompt = (
            f"Analyze the following hotel-related text and return a JSON object with keys: "
            f"'category', 'sentiment', and 'entities' (if any):\n{text}"
        )
        output = cls._ask_model(prompt, max_tokens=300)
        try:
            return eval(output)
        except Exception:
            return {"category": "general", "sentiment": "neutral", "entities": {}}