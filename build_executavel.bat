@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   Gerando executavel X GAMES para a loja
echo ============================================
echo.

py -m pip install pyinstaller streamlit pandas fpdf2 requests pyodbc -q
if errorlevel 1 (
    echo Erro ao instalar dependencias.
    pause
    exit /b 1
)

echo Compilando... (pode demorar alguns minutos)
py -m PyInstaller --noconfirm --onedir --name X-GAMES ^
  --collect-all streamlit ^
  --collect-all pandas ^
  --collect-all altair ^
  --collect-all pydeck ^
  --collect-all tornado ^
  --hidden-import=pyodbc ^
  --hidden-import=fpdf ^
  --hidden-import=streamlit.web.cli ^
  --hidden-import=streamlit.runtime.scriptrunner ^
  src\launcher.py

if errorlevel 1 (
    echo Erro na compilacao.
    pause
    exit /b 1
)

echo Copiando arquivos do sistema...
copy /Y src\app.py dist\X-GAMES\
copy /Y src\saros_theme.py dist\X-GAMES\
copy /Y src\db.py dist\X-GAMES\
copy /Y src\utils.py dist\X-GAMES\
copy /Y src\reports.py dist\X-GAMES\
copy /Y src\dataBase.py dist\X-GAMES\
copy /Y src\importar_access.py dist\X-GAMES\
xcopy /E /I /Y data dist\X-GAMES\data\
xcopy /E /I /Y .streamlit dist\X-GAMES\.streamlit\
copy /Y LEIA-ME-LOJA.txt dist\X-GAMES\
copy /Y LEIA-ME-BLOQUEIO-WINDOWS.txt dist\X-GAMES\

echo.
echo ============================================
echo   PRONTO!
echo   Pasta: dist\X-GAMES\
echo   Execute: X-GAMES.exe
echo.
echo   Copie a pasta inteira "X-GAMES" para o PC da loja.
echo ============================================
