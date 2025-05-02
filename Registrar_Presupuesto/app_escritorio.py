import webview # Asegúrate de tener instalada la librería webview
import subprocess
import threading
import os

def iniciar_servidor_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Presupuesto_Familiar.settings')  # reemplaza 'nombre_proyecto'
    subprocess.Popen(['python', 'manage.py', 'runserver', '127.0.0.1:8000'])

def lanzar_app():
    webview.create_window("Mi Aplicación Django", "http://127.0.0.1:8000")
    webview.start()

if __name__ == '__main__':
    threading.Thread(target=iniciar_servidor_django).start()
    lanzar_app()
