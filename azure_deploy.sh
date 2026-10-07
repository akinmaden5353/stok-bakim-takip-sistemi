#!/bin/bash
set -e

echo "======================================================================"
echo "   STOK VE MAKİNE BAKIM TAKİP SİSTEMİ - AZURE DAĞITIM SİHİRBAZI"
echo "======================================================================"
echo ""

# Azure CLI Check
if ! command -v az &> /dev/null; then
    echo "[HATA] Azure CLI (az) bulunamadı! Lütfen Azure CLI kurunuz."
    exit 1
fi

RANDOM_ID=$((RANDOM % 9000 + 1000))
LOCATION="westeurope"
RG_NAME="rg-stok-bakim"
PLAN_NAME="asp-stok-bakim"
APP_NAME="app-stok-bakim-$RANDOM_ID"
PG_SERVER="pg-stok-bakim-$RANDOM_ID"
PG_DB="bakim_db"
PG_USER="bakimadmin"
PG_PASSWORD="BakimTakip2026!Secured"

echo "[*] Kaynak Grubu oluşturuluyor: $RG_NAME..."
az group create --name "$RG_NAME" --location "$LOCATION"

echo "[*] Azure PostgreSQL Flexible Server kuruluyor..."
az postgres flexible-server create \
    --resource-group "$RG_NAME" \
    --name "$PG_SERVER" \
    --location "$LOCATION" \
    --admin-user "$PG_USER" \
    --admin-password "$PG_PASSWORD" \
    --database-name "$PG_DB" \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --yes

echo "[*] Güvenlik duvarı ayarlanıyor..."
az postgres flexible-server firewall-rule create \
    --resource-group "$RG_NAME" \
    --name "$PG_SERVER" \
    --rule-name AllowAllAzureServicesAndIPs \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 255.255.255.255

DATABASE_URL="postgresql://${PG_USER}:${PG_PASSWORD}@${PG_SERVER}.postgres.database.azure.com:5432/${PG_DB}?sslmode=require"

echo "[*] App Service Plan ve Web App oluşturuluyor..."
az appservice plan create \
    --name "$PLAN_NAME" \
    --resource-group "$RG_NAME" \
    --is-linux \
    --sku B1 \
    --location "$LOCATION"

az webapp create \
    --name "$APP_NAME" \
    --plan "$PLAN_NAME" \
    --resource-group "$RG_NAME" \
    --runtime "PYTHON:3.11" \
    --startup-file "startup.sh"

echo "[*] Ortam değişkenleri tanımlanıyor..."
az webapp config appsettings set \
    --name "$APP_NAME" \
    --resource-group "$RG_NAME" \
    --settings \
        DATABASE_URL="$DATABASE_URL" \
        WEBSITES_PORT="8000" \
        AUTO_SEED="true" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true"

echo "[*] Kodlar yükleniyor..."
az webapp up \
    --name "$APP_NAME" \
    --resource-group "$RG_NAME" \
    --plan "$PLAN_NAME" \
    --location "$LOCATION" \
    --runtime "PYTHON:3.11"

echo ""
echo "======================================================================"
echo "   AZURE DAĞITIMI TAMAMLANDI!"
echo "   Canlı Adres: https://${APP_NAME}.azurewebsites.net"
echo "======================================================================"
