import pytest
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

MODEL_PATH = os.path.join(os.getcwd(), "finetunedmodel-merged")

@pytest.fixture(scope="session")
def tokenizer():
    return AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)

@pytest.fixture(scope="session")
def model():
    return AutoModelForCausalLM.from_pretrained(MODEL_PATH, local_files_only=True)