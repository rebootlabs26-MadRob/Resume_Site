#!/bin/bash
# Mad_SPHub Backup Script
# Run daily to backup configs and data

BACKUP_DIR="/home/mastersurface/Projects/Backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="mad_sphub_backup_${DATE}"

mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

echo "=== Mad_SPHub Backup Starting ==="

# Backup Docker configs
echo "Backing up Docker configs..."
cp ~/docker-compose.yml "${BACKUP_DIR}/${BACKUP_NAME}/"
cp ~/telegraf/telegraf.conf "${BACKUP_DIR}/${BACKUP_NAME}/"
cp ~/mosquitto/config/mosquitto.conf "${BACKUP_DIR}/${BACKUP_NAME}/"

# Backup InfluxDB data
echo "Backing up InfluxDB..."
docker exec influxdb influx backup /tmp/influx_backup -t RBL_SuperToken_2024
docker cp influxdb:/tmp/influx_backup "${BACKUP_DIR}/${BACKUP_NAME}/influxdb_backup"
docker exec influxdb rm -rf /tmp/influx_backup

# Backup project files
echo "Backing up project files..."
cp -r ~/Projects "${BACKUP_DIR}/${BACKUP_NAME}/"

# Create archive
echo "Creating archive..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"

# Keep only last 7 backups
echo "Cleaning old backups..."
ls -t ${BACKUP_DIR}/*.tar.gz | tail -n +8 | xargs -r rm

echo "=== Backup Complete: ${BACKUP_NAME}.tar.gz ==="
