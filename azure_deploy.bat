@echo off
chcp 65001 >nul
title Microsoft Azure Otomatik Dagitim Araci - Stok ve Makine Bakim

echo ======================================================================
echo    STOK VE MAKINE BAKIM TAKIP SISTEMI - AZURE DAGITIM SIHIRBAZI
echo ======================================================================
echo.

:: 1. Azure CLI Kontrolu
az version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Azure CLI (az) bilgisayarinizda bulunamadi!
    echo Lutfen https://aka.ms/installazurecliwindows adresinden Azure CLI yukleyiniz.
    pause
    exit /b 1
)

echo [*] Azure hesabina baglaniliyor...
call az account show >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Lutfen acilan tarayici penceresinden Azure hesabiniza giris yapin.
    call az login
)

:: Degiskenler
set RANDOM_ID=%RANDOM%
set LOCATION=westeurope
set RG_NAME=rg-stok-bakim
set PLAN_NAME=asp-stok-bakim
set APP_NAME=app-stok-bakim-%RANDOM_ID%
set PG_SERVER=pg-stok-bakim-%RANDOM_ID%
set PG_DB=bakim_db
set PG_USER=bakimadmin
set PG_PASSWORD=BakimTakip2026!Secured

echo.
echo [*] Dagitim Parametreleri:
echo    - Bolge (Location)         : %LOCATION%
echo    - Kaynak Grubu (RG)        : %RG_NAME%
echo    - Web App Adi              : %APP_NAME%
echo    - PostgreSQL Sunucu Adi    : %PG_SERVER%
echo    - PostgreSQL Veritabani    : %PG_DB%
echo ======================================================================
echo.

:: 2. Kaynak Grubu Olusturma
echo [1/4] Kaynak Grubu (Resource Group) olusturuluyor: %RG_NAME%...
call az group create --name %RG_NAME% --location %LOCATION% >nul

:: 3. Azure Database for PostgreSQL Flexible Server Olusturma
echo [2/4] Azure PostgreSQL Flexible Server kuruluyor (birkac dakika surebilir)...
call az postgres flexible-server create ^
    --resource-group %RG_NAME% ^
    --name %PG_SERVER% ^
    --location %LOCATION% ^
    --admin-user %PG_USER% ^
    --admin-password %PG_PASSWORD% ^
    --database-name %PG_DB% ^
    --sku-name Standard_B1ms ^
    --tier Burstable ^
    --storage-size 32 ^
    --yes >nul

:: Azure icinden erisim icin guvenlik duvari kurali acma (Allow Azure Services)
echo [*] PostgreSQL guvenlik duvari kurallari tanimlaniyor...
call az postgres flexible-server firewall-rule create ^
    --resource-group %RG_NAME% ^
    --name %PG_SERVER% ^
    --rule-name AllowAllAzureServicesAndIPs ^
    --start-ip-address 0.0.0.0 ^
    --end-ip-address 255.255.255.255 >nul

set DATABASE_URL=postgresql://%PG_USER%:%PG_PASSWORD%@%PG_SERVER%.postgres.database.azure.com:5432/%PG_DB%?sslmode=require

:: 4. App Service Plan ve Web App Olusturma
echo [3/4] Linux App Service ve Web App olusturuluyor...
call az appservice plan create ^
    --name %PLAN_NAME% ^
    --resource-group %RG_NAME% ^
    --is-linux ^
    --sku B1 ^
    --location %LOCATION% >nul

call az webapp create ^
    --name %APP_NAME% ^
    --plan %PLAN_NAME% ^
    --resource-group %RG_NAME% ^
    --runtime "PYTHON:3.11" ^
    --startup-file "startup.sh" >nul

:: 5. Ortam Degiskenlerini (App Settings) Tanimlama
echo [4/4] Uygulama ayarlari (DATABASE_URL, WEBSITES_PORT, AUTO_SEED) yukleniyor...
call az webapp config appsettings set ^
    --name %APP_NAME% ^
    --resource-group %RG_NAME% ^
    --settings ^
        DATABASE_URL="%DATABASE_URL%" ^
        WEBSITES_PORT="8000" ^
        AUTO_SEED="true" ^
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" >nul

:: 6. Kodu Yukleme (Deploy)
echo [*] Kaynak kodlari Azure Web App'e yukleniyor...
call az webapp up ^
    --name %APP_NAME% ^
    --resource-group %RG_NAME% ^
    --plan %PLAN_NAME% ^
    --location %LOCATION% ^
    --runtime "PYTHON:3.11"

echo.
echo ======================================================================
echo    TEBRIKLER! AZURE DAGITIMI BASARIYLA TAMAMLANDI!
echo ======================================================================
echo  Canli Web Adresiniz: https://%APP_NAME%.azurewebsites.net
echo  Saglik Kontrolu    : https://%APP_NAME%.azurewebsites.net/api/health
echo  API Dokumantasyonu : https://%APP_NAME%.azurewebsites.net/docs
echo ======================================================================
echo.
pause


