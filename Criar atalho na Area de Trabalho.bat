@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "PASTA_EXE=%~dp0dist\X-GAMES"
set "EXE=%PASTA_EXE%\X-GAMES.exe"
set "ATALHO=%USERPROFILE%\Desktop\X GAMES.lnk"

if not exist "%EXE%" (
    echo.
    echo  Nao encontrei o executavel em:
    echo  %EXE%
    echo.
    echo  Rode primeiro: build_executavel.bat
    echo.
    pause
    exit /b 1
)

powershell -NoProfile -Command ^
  "$s = New-Object -ComObject WScript.Shell; ^
   $l = $s.CreateShortcut('%ATALHO%'); ^
   $l.TargetPath = '%EXE%'; ^
   $l.WorkingDirectory = '%PASTA_EXE%'; ^
   $l.Description = 'X GAMES - Sistema de Ordens de Servico'; ^
   $l.Save()"

echo.
echo  Atalho criado na Area de Trabalho: "X GAMES"
echo.
echo  Duplo clique no atalho para abrir o sistema.
echo  (A pasta dist\X-GAMES deve continuar no lugar - nao apague.)
echo.
pause
