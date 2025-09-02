@echo off
echo 🚀 Resume Analyzer Installation Script for Windows
echo ================================================

echo.
echo 🔄 Upgrading pip and build tools...
python -m pip install --upgrade pip setuptools wheel

echo.
echo 🔄 Installing core dependencies...
pip install python-dotenv
pip install numpy
pip install azure-core
pip install openai
pip install chainlit

echo.
echo 🔄 Installing Azure Document Intelligence...
pip install azure-ai-documentintelligence

echo.
echo ================================================
echo 🎉 Installation completed!
echo.
echo Next steps:
echo 1. Update your .env file with Azure credentials
echo 2. Run: chainlit run chainlit_app.py -w
echo 3. Open http://localhost:8000 in your browser
echo.
pause