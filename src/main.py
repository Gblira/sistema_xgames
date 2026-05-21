import os
import subprocess
import sys

def iniciar_sistema():
    print("🚀 Iniciando X-GAMES...")
    base_path = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_path, "app.py")
    db_setup_path = os.path.join(base_path, "dataBase.py")

    print("📂 Verificando banco de dados...")
    subprocess.run([sys.executable, db_setup_path], check=False)

    print("🌐 Abrindo interface...")
    try:
        subprocess.run([
    sys.executable, "-m", "streamlit", "run", app_path,
    "--browser.gatherUsageStats=false",
    "--server.headless=true"
    ])
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")
        print("💡 Instale as dependências: py -m pip install -r requirements.txt")


if __name__ == "__main__":
    iniciar_sistema()
