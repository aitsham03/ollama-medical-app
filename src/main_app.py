import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                            QLineEdit, QTextEdit, QLabel, QFileDialog, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal
import requests
import json
from pathlib import Path
import PyPDF2

class OllamaInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.ollama_url = "http://localhost:11434"
        self.initUI()
        self.pdf_path = None

    def initUI(self):
        self.setWindowTitle("Analyse Médicale avec Ollama")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        # PDF Selection
        self.pdf_file_label = QLabel("Sélectionner le fichier PDF à analyser :")
        self.pdf_file_input = QLineEdit()
        self.pdf_file_input.setReadOnly(True)
        self.browse_button = QPushButton("Parcourir...")
        self.browse_button.clicked.connect(self.browse_pdf)

        # Question Section
        self.question_label = QLabel("Question pour l'analyse :")
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ex: Le patient a-t-il du diabète? Précisez le type.")
        self.ask_button = QPushButton("Analyser le document")
        self.ask_button.clicked.connect(self.ask_question)
        self.ask_button.setEnabled(False)

        # Response Area
        self.response_label = QLabel("Réponse :")
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)

        # Add widgets to layout
        layout.addWidget(self.pdf_file_label)
        layout.addWidget(self.pdf_file_input)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.question_label)
        layout.addWidget(self.question_input)
        layout.addWidget(self.ask_button)
        layout.addWidget(self.response_label)
        layout.addWidget(self.response_text)

    def browse_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier PDF", "", "PDF Files (*.pdf)")
        
        if file_path:
            self.pdf_path = file_path
            self.pdf_file_input.setText(Path(file_path).name)
            self.ask_button.setEnabled(True)

    def ask_question(self):
        if not self.pdf_path or not Path(self.pdf_path).exists():
            QMessageBox.warning(self, "Erreur", "Fichier PDF invalide ou introuvable")
            return

        question = self.question_input.text().strip()
        if not question:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une question")
            return

        self.ask_button.setEnabled(False)
        self.response_text.setPlainText("Analyse en cours...")

        self.thread = AskQuestionThread(self.ollama_url, self.pdf_path, question)
        self.thread.response_signal.connect(self.handle_response)
        self.thread.error_signal.connect(self.handle_error)
        self.thread.finished.connect(self.thread_finished)
        self.thread.start()

    def handle_response(self, response):
        self.response_text.setPlainText(response)

    def handle_error(self, error_msg):
        QMessageBox.critical(self, "Erreur", error_msg)
        self.response_text.setPlainText("Erreur lors de l'analyse")

    def thread_finished(self):
        self.ask_button.setEnabled(True)

class AskQuestionThread(QThread):
    response_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, ollama_url, pdf_path, question):
        super().__init__()
        self.ollama_url = ollama_url
        self.pdf_path = pdf_path
        self.question = question

    def run(self):
        try:
            # 1. Extraire le texte du PDF
            text = self.extract_text_from_pdf()
            
            # 2. Préparer le prompt
            prompt = self.create_prompt(text)
            
            # 3. Envoyer la requête à Ollama
            response = self.query_ollama(prompt)
            
            self.response_signal.emit(response)
            
        except Exception as e:
            self.error_signal.emit(f"Erreur lors du traitement : {str(e)}")

    def extract_text_from_pdf(self):
        """Extrait le texte d'un fichier PDF"""
        try:
            text = ""
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Erreur d'extraction PDF: {str(e)}")

    def create_prompt(self, text):
        return f"""
        [Rôle] Vous êtes un assistant médical expert en diabétologie.
        [Consignes]
        - Analysez ce compte rendu médical
        - Répondez à la question posée
        - Structurez votre réponse
        - Précisez le type de diabète (1, 2, gestationnel)
        - Distinguez entre antécédents et condition actuelle

        [Compte rendu]
        {text}

        [Question]
        {self.question}
        """

    def query_ollama(self, prompt):
        """Utilise l'API REST d'Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama2",  # ou un modèle médical finetuné
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "Pas de réponse obtenue")
        except Exception as e:
            raise Exception(f"Erreur de communication avec Ollama: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Vérifier que PyPDF2 est installé
    try:
        import PyPDF2
    except ImportError:
        QMessageBox.critical(None, "Erreur", 
            "Le module PyPDF2 est requis. Installez-le avec : pip install PyPDF2")
        sys.exit(1)
    
    # Vérifier qu'Ollama est en cours d'exécution
    try:
        response = requests.get("http://localhost:11434", timeout=2)
    except:
        QMessageBox.critical(None, "Erreur", 
            "Ollama ne semble pas être en cours d'exécution.\n"
            "Veuillez démarrer Ollama avec la commande : ollama serve")
        sys.exit(1)

    interface = OllamaInterface()
    interface.show()
    sys.exit(app.exec_())