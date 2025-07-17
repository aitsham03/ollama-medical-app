# Ignorer les environnements virtuels
venv/
.venv/

# Ignorer les caches Python
__pycache__/
*.pyc

# Ignorer les dossiers de build de PyInstaller et les fichiers générés
src/build/   # <-- Chemin corrigé
src/dist/    # <-- Chemin corrigé
src/*.spec   # <-- Chemin corrigé (si le .spec est à la racine de src)

# Fichiers spécifiques aux OS
.DS_Store
Thumbs.db