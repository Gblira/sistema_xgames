"""
Inicia o X GAMES e abre o navegador.
Usado pelo executavel (.exe) ou manualmente: py launcher.py
"""
import os
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path


def diretorio_app():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def caminho_app():
    base = diretorio_app()
    for candidato in (base / "app.py", base / "src" / "app.py"):
        if candidato.exists():
            return candidato
    raise FileNotFoundError(f"app.py nao encontrado em {base}")


def aguardar_e_abrir_navegador(url, tentativas=60):
    import urllib.request

    for _ in range(tentativas):
        time.sleep(0.5)
        try:
            urllib.request.urlopen(url, timeout=1)
            webbrowser.open(url)
            print(f"Navegador aberto em {url}")
            return
        except OSError:
            continue
    print(f"Abra manualmente no navegador: {url}")


def rodar_streamlit_exe(app_py, porta):
    """No .exe o sys.executable e o proprio X-GAMES.exe — roda Streamlit por dentro."""
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

    url = f"http://localhost:{porta}"
    threading.Thread(
        target=aguardar_e_abrir_navegador, args=(url,), daemon=True
    ).start()

    sys.argv = [
        "streamlit",
        "run",
        str(app_py),
        f"--server.port={porta}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
    ]

    from streamlit.web import cli as stcli

    stcli.main()


def rodar_streamlit_dev(app_py, porta):
    """Modo desenvolvimento com Python instalado."""
    env = os.environ.copy()
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"

    url = f"http://localhost:{porta}"

    processo = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_py),
            f"--server.port={porta}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ],
        env=env,
        cwd=str(app_py.parent),
    )

    aguardar_e_abrir_navegador(url)

    try:
        processo.wait()
    except KeyboardInterrupt:
        processo.terminate()


def main():
    app_py = caminho_app()
    os.chdir(app_py.parent)
    os.makedirs(diretorio_app() / "data", exist_ok=True)

    porta = "8501"

    print("Iniciando X GAMES...")
    print(f"Pasta: {app_py.parent}")
    print("Aguarde o navegador abrir...")
    print("Feche esta janela para encerrar o sistema.\n")

    if getattr(sys, "frozen", False):
        rodar_streamlit_exe(app_py, porta)
    else:
        rodar_streamlit_dev(app_py, porta)


if __name__ == "__main__":
    main()
