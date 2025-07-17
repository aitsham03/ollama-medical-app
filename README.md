<h1 align="center">
📄 Ollama Medical App: Your Medical Report Analysis Assistant 🩺
</h1>
</p>
<p align="center">
<a href="https://github.com/your_username/ollama-medical-app">

🌟 Description

Ollama Medical App is a powerful and intuitive desktop application designed to simplify the analysis of medical reports in PDF format. Developed with PyQt6, it leverages the power of Large Language Models (LLM) by running the Mistral model locally via Ollama. This ensures complete confidentiality of your medical data and fast responses, without relying on external cloud services.

The application allows you to load a PDF, extract its text, ask specific questions to the model, and obtain relevant information, all from a responsive interface.

✨ Key Features
PDF Loading and Preview : Easily import your medical report PDFs and visualize the extracted text.

Context Editing : Modify the extracted text from the PDF directly in the interface to refine the context sent to the model, optimizing performance and response relevance.

Local LLM Querying : Ask precise questions to the Mistral model (via Ollama) about the document's content.

Responsive User Interface : The application remains fluid and responsive even while the model processes complex queries, thanks to the use of background threads.

Robust Error Handling : Clear messages and notifications guide you in case of issues (Ollama connection, timeout, etc.).

🚀 Installation
To get this application up and running, follow these simple steps:

Prerequisites
Python 3.x (version 3.10 or higher recommended).

Ollama : The runtime for language models. Download and install Ollama from their official website: https://ollama.com/download.

Ensure Ollama is running and active in the background on your machine.

Mistral Model : The application uses the mistral model. Open a terminal or command prompt and download the model: ollama pull mistral


Python Dependencies
Clone the repository :

git clone https://github.com/aitsham03/ollama-medical-app
cd ollama-medical-app

Create and activate a virtual environment (highly recommended to isolate dependencies) :

python -m venv venv
# On Windows :
.\venv\Scripts\activate
# On macOS/Linux :
source venv/bin/activate


Install the necessary Python dependencies :

pip install -r requirements.txt


The requirements.txt file should contain:

PyQt6
PyPDF2
requests


💡 Usage
Launch the application and start analyzing your documents!

Launch the Application :

python src/main_app.py

Main Steps :

Upload a PDF : Click the "Upload le PDF" button and select your medical report. The extracted text will appear in the text area.

Adjust Context (optional) : If the document is very long or you want to target specific information, you can edit the displayed text in the "Extrait du PDF" area before asking your question.

Ask a Question : Type your question into the dedicated field.

Get the Answer : Click "Poser la question" and await the model's response, which will appear in the lower area.


📦 Download the Application (Windows Executable)
For quick use without Python installation, you can download the Windows executable (.exe) directly from the Releases page of this repository.

(Please note that you will still need to install Ollama and download the 'mistral' model separately for the application to function.)


📂 Project Structure

Je comprends parfaitement votre frustration concernant l'affichage de la structure du projet. Il semble que le rendu Markdown dans votre environnement de chat ne gère pas correctement les sauts de ligne pour cette section spécifique.

Voici uniquement le texte corrigé pour la section "Project Structure" que vous devriez ajouter à votre fichier README.md :

Markdown

## 📂 Project Structure

- **main_app.py** : the python code defining the app
- **OllamaMedicalApp.exe** : an executable that launch the app

⚠️ Troubleshooting
"Unable to connect to Ollama" / "Ollama request timed out" :

Ensure Ollama is running on your system.

Make sure the mistral model is correctly downloaded (ollama pull mistral).

If the document is very long, try reducing the text in the editing area before asking the question. Your machine might lack RAM/VRAM for very large documents.

"QWindowsNativeFileDialogBase::shellItem : Unhandled scheme: "data"" :

This error is often related to the Windows environment. Try updating PyQt6 (pip install --upgrade PyQt6) or running the application from a standard command prompt (rather than an IDE). A system restart can sometimes resolve the issue.


📄 License
