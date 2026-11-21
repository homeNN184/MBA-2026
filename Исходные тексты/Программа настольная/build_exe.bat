@echo off
chcp 65001 >nul
echo === Сборка настольной программы в один файл ===
echo.
python --version
if errorlevel 1 (
  echo Python не найден. Установите Python 3.9 или новее с сайта python.org
  echo и при установке отметьте пункт "Add python.exe to PATH".
  pause
  exit /b 1
)
echo Установка требуемых пакетов ...
python -m pip install --upgrade pip
python -m pip install --upgrade openpyxl pyinstaller
if errorlevel 1 (
  echo Не удалось установить пакеты.
  pause
  exit /b 1
)
echo Сборка ...
python -m PyInstaller --noconfirm --clean TRL_Model.spec
if errorlevel 1 (
  echo Сборка завершилась с ошибкой.
  pause
  exit /b 1
)
echo.
echo Готово. Файл: dist\TRL_Model.exe
echo Файл можно переименовать и перенести на другой компьютер с Windows.
pause
