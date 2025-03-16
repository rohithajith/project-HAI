import os
import requests

# Define the model URL
model_url = "https://huggingface.co/rohith0990/finetunedmodel-merged/model.tar.gz"

# Define the output directory
output_dir = "finetunedmodel-merged"

# Download the model
os.makedirs(output_dir, exist_ok=True)
response = requests.get(model_url)
with open(os.path.join(output_dir, "model.tar.gz"), "wb") as f:
    f.write(response.content)

# Test the model with a sample message
sample_message = "Hello, how are you?"

# Add your code to load the model and use it to process the sample message
# This is just a placeholder, you will need to replace it with the actual code to load the model and process the message
print("Processing message:", sample_message)

# Save the output to a file
with open(os.path.join(output_dir, "output.txt"), "w") as f:
    f.write("Output:\n")
    f.write("Model output: This is a placeholder output\n")