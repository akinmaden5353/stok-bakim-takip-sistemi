@echo off
chcp 65001 >nul
title Stok ve Makine Bakim Takip Sistemi

echo ========================================================
echo   STOK VE MAKİNE BAKIM TAKİP SİSTEMİ
echo   Yerel Ağ (LAN) Sunucusu Başlatılıyor...
echo ========================================================
echo.

:: Check python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi! Lutfen Python 3.10 veya uzeri yukleyin.
    pause
    exit /b 1
)

:: Run database seed if db does not exist
if not exist "data\maintenance.db" (
    echo Veritabani bulunamadi, ornek veriler yukleniyor...
    python seed_data.py
    echo.
)

echo Sunucu baslatiliyor (Cikis icin Ctrl+C basiniz)...
echo.
python main.py

pause
