@echo off
chcp 65001 >nul
title Stok ve Makine Bakim Takip Sistemi

echo ========================================================
echo   STOK VE MAKİNE BAKIM TAKİP SİSTEMİ
echo   Yerel Sunucu Başlatılıyor...
echo ========================================================
echo.

:: 1. Python Kontrolü
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi! Lutfen Python 3.10 veya uzerini yukleyip PATH'e ekleyin.
    pause
    exit /b 1
)

:: 2. Gerekli Kütüphanelerin Kontrolü
python -c "import fastapi, uvicorn, sqlalchemy, pydantic" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Gerekli kutuphaneler yukleniyor (bu islem ilk seferde 1-2 dakika surebilir)...
    pip install -r requirements.txt
)

:: 3. Veritabanı Kontrolü ve Örnek Veri Yükleme
if not exist "data\maintenance.db" (
    echo [*] Ilk kurulum: ornek veriler veritabanina yukleniyor...
    python seed_data.py
    echo.
)

:: 4. Tarayıcıyı 2 saniye sonra otomatik aç
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000"

echo [*] Sunucu baslatildi!
echo [*] Tarayiciniz otomatik olarak acilacaktir (http://localhost:8000)
echo [*] Kapatmak icin bu pencereyi kapatabilir veya Ctrl+C yapabilirsiniz.
echo ========================================================
echo.
python main.py

pause
