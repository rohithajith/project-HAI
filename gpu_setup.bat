@echo off

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install PyTorch with CUDA 12.4
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

REM Install bitsandbytes for Windows
pip install bitsandbytes-cuda110 bitsandbytes

REM Install accelerate
pip install accelerate
pip install transformers
pip install -r requirements.txt

python .\download_hfmodel.py
python .\backend\local_model_chatbot.py
python .\teste.py
echo Setup Complete.
pause