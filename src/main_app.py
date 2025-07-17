import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

import PyPDF2 # ou 'pypdf'

# --- Nouvelle classe pour exécuter la requête Ollama dans un thread séparé ---
class OllamaWorker(QThread):
    # Signaux personnalisés pour communiquer avec le thread principal de l'UI
    finished = pyqtSignal(str) # Émet la réponse du modèle
    error = pyqtSignal(str)    # Émet un message d'erreur
    started_processing = pyqtSignal() # Émet quand le traitement commence

    def __init__(self, prompt_text, parent=None):
        super().__init__(parent)
        self.prompt_text = prompt_text
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "mistral"

    def run(self):
        # Cette méthode est exécutée lorsque le thread est démarré
        self.started_processing.emit() # Informe l'UI que le traitement commence

        payload = {
            "model": self.model,
            "prompt": self.prompt_text,
            "stream": False
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=600) # Timeout de 5 minutes
            response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP

            result = response.json()
            if "response" in result:
                self.finished.emit(result["response"].strip())
            else:
                self.error.emit("Réponse inattendue de Ollama.")

        except requests.exceptions.ConnectionError:
            self.error.emit("Impossible de se connecter à Ollama. Assurez-vous que Ollama est en cours d'exécution et que le modèle 'mistral' est téléchargé.")
        except requests.exceptions.Timeout:
            self.error.emit("La requête à Ollama a expiré. Le modèle prend peut-être trop de temps à répondre ou le document est trop long.")
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Une erreur réseau/API s'est produite lors de la requête Ollama: {e}")
        except Exception as e:
            self.error.emit(f"Une erreur inattendue s'est produite: {e}")

class OllamaPDFQueryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.pdf_text = "" # Stocke le texte original du PDF
        self.ollama_worker = None # Pour garder une référence au thread
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Ollama PDF App - Comptes rendu médicaux")
        self.setGeometry(100, 100, 800, 700)

        main_layout = QVBoxLayout()

        # --- Section Upload PDF ---
        pdf_layout = QHBoxLayout()
        self.pdf_path_label = QLabel("Aucun fichier PDF sélectionné")
        self.upload_button = QPushButton("Upload le PDF")
        self.upload_button.clicked.connect(self.upload_pdf)
        pdf_layout.addWidget(self.pdf_path_label)
        pdf_layout.addWidget(self.upload_button)
        main_layout.addLayout(pdf_layout)

        # --- Section Affichage Texte PDF (maintenant éditable !) ---
        main_layout.addWidget(QLabel("Extrait du PDF (vous pouvez le modifier pour réduire le contexte envoyé au modèle) :"))
        self.pdf_content_display = QTextEdit()
        # self.pdf_content_display.setReadOnly(True) # <-- C'est cette ligne qui a été commentée
        self.pdf_content_display.setPlaceholderText("Le texte extrait du PDF s'affichera ici. Vous pouvez le modifier pour réduire le contexte envoyé au modèle.")
        main_layout.addWidget(self.pdf_content_display)

        # --- Section Question à Ollama ---
        main_layout.addWidget(QLabel("Posez votre question au modèle :"))
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ex: Le patient a-t-il du diabète ? Y a-t-il des allergies mentionnées ?")
        main_layout.addWidget(self.question_input)

        self.query_button = QPushButton("Poser la question")
        self.query_button.clicked.connect(self.query_ollama)
        main_layout.addWidget(self.query_button)

        # --- Barre de progression / Indicateur de chargement ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Mode indéterminé (barre qui "bouge")
        self.progress_bar.hide() # Cachée par défaut
        main_layout.addWidget(self.progress_bar)

        # --- Section Réponse d'Ollama ---
        main_layout.addWidget(QLabel("Réponse du modèle :"))
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        self.response_display.setPlaceholderText("La réponse du modèle s'affichera ici...")
        main_layout.addWidget(self.response_display)

        self.setLayout(main_layout)

    def upload_pdf(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Sélectionner un fichier PDF", "", "PDF Files (*.pdf)")

        if file_path:
            self.pdf_path_label.setText(f"Fichier sélectionné: {file_path}")
            try:
                self.pdf_text = self.extract_text_from_pdf(file_path)
                self.pdf_content_display.setText(self.pdf_text) # Affiche le texte complet
                QMessageBox.information(self, "PDF Uploadé", "Texte du PDF extrait avec succès.\nVous pouvez maintenant modifier le texte affiché pour réduire le contexte envoyé au modèle et améliorer les performances.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur PDF", f"Impossible d'extraire le texte du PDF: {e}")
                self.pdf_text = ""
                self.pdf_content_display.clear()
        else:
            self.pdf_path_label.setText("Aucun fichier PDF sélectionné")
            self.pdf_text = ""
            self.pdf_content_display.clear()

    def extract_text_from_pdf(self, pdf_path):
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"
        return text

    def query_ollama(self):
        question = self.question_input.text().strip()
        # Récupérer le texte ACTUELLEMENT affiché et potentiellement modifié par l'utilisateur
        current_pdf_context = self.pdf_content_display.toPlainText().strip()

        if not current_pdf_context:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord uploader un fichier PDF ou vous avez vidé le texte du PDF.")
            return

        if not question:
            QMessageBox.warning(self, "Erreur", "Veuillez poser une question.")
            return

        # Prompt pour le modèle, utilisant le texte potentiellement réduit par l'utilisateur
        prompt = (
            "Tu es un expert médical et un assistant de lecture de comptes rendus d'hospitalisation. "
            "Ton rôle est d'analyser le compte rendu fourni et de répondre précisément aux questions posées. "
            "Si l'information n'est pas clairement présente dans le texte, indique-le. "
            "Sois concis, clair et direct dans tes réponses. "
            "Voici le compte rendu d'hospitalisation (potentiellement réduit par l'utilisateur) :\n\n"
            f"```text\n{current_pdf_context}\n```\n\n" # Utilise le texte modifié
            f"Question : {question}"
        )

        # Désactiver le bouton et montrer la barre de progression
        self.query_button.setEnabled(False)
        self.progress_bar.show()
        self.response_display.setText("Envoi de la requête à Ollama... Veuillez patienter.")

        # Créer et démarrer le worker thread
        self.ollama_worker = OllamaWorker(prompt)
        # Connecter les signaux du worker aux slots de notre UI
        self.ollama_worker.started_processing.connect(self.on_ollama_processing_started)
        self.ollama_worker.finished.connect(self.on_ollama_response_received)
        self.ollama_worker.error.connect(self.on_ollama_error)
        self.ollama_worker.start() # Lance l'exécution de la méthode run() dans un nouveau thread

    def on_ollama_processing_started(self):
        # Cette fonction est appelée quand le worker commence son travail
        self.response_display.setText("Envoi de la requête à Ollama... Veuillez patienter.")
        self.progress_bar.show()
        self.query_button.setEnabled(False)


    def on_ollama_response_received(self, response_text):
        # Cette fonction est appelée lorsque le worker a terminé et a une réponse
        self.response_display.setText(response_text)
        self.reset_ui_state()

    def on_ollama_error(self, error_message):
        # Cette fonction est appelée si le worker rencontre une erreur
        QMessageBox.critical(self, "Erreur Ollama", error_message)
        self.response_display.setText(f"Erreur: {error_message}")
        self.reset_ui_state()

    def reset_ui_state(self):
        # Réinitialise l'état de l'UI après la fin ou l'erreur du traitement
        self.query_button.setEnabled(True)
        self.progress_bar.hide()
        self.ollama_worker = None # Libère la référence au worker

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OllamaPDFQueryApp()
    ex.show()
    sys.exit(app.exec())