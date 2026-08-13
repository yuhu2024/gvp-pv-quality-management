#!/bin/bash
# ==============================================================
# 君合盟药物警戒培训管理系统 - 每日自动备份脚本
# 添加到 crontab: sudo crontab -e
# 每日凌晨2点执行: 0 2 * * * /opt/training_system/deploy/backup.sh
# ==============================================================

set -e

# ===== 配置 =====
PROJECT_NAME="training_system"
PROJECT_DIR="/opt/${PROJECT_NAME}"
BACKUP_DIR="/backup/${PROJECT_NAME}"
DB_NAME="training_db"
RETENTION_DAYS=30

# 时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# ===== 颜色 =====
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# ===== 日志 =====
log_info()  { echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"; }

# ===== 检查目录 =====
mkdir -p ${BACKUP_DIR}/{db,media,logs}

# ===== 1. 备份数据库 =====
backup_database() {
    log_info "开始备份数据库..."
    
    # 从 .env 读取数据库密码
    if [ -f "${PROJECT_DIR}/.env" ]; then
        export $(grep -E '^DB_' ${PROJECT_DIR}/.env | xargs)
    fi
    
    DB_FILE="${BACKUP_DIR}/db/${DB_NAME}_${TIMESTAMP}.sql.gz"
    
    # 使用 pg_dump 备份
    PGPASSWORD="${DB_PASSWORD}" pg_dump \
        -h "${DB_HOST:-localhost}" \
        -U "${DB_USER:-training_user}" \
        -d "${DB_NAME}" \
        --no-owner \
        --no-acl \
        | gzip > "${DB_FILE}"
    
    # 验证备份文件
    if [ -f "${DB_FILE}" ] && [ -s "${DB_FILE}" ]; then
        FILE_SIZE=$(du -h "${DB_FILE}" | cut -f1)
        log_info "数据库备份完成: ${DB_FILE} (${FILE_SIZE})"
    else
        log_error "数据库备份失败!"
        return 1
    fi
}

# ===== 2. 备份媒体文件（上传的PPT/Word/视频） =====
backup_media() {
    log_info "开始备份媒体文件..."
    
    MEDIA_SRC="${PROJECT_DIR}/media"
    MEDIA_DEST="${BACKUP_DIR}/media/${TIMESTAMP}"
    
    if [ -d "${MEDIA_SRC}" ] && [ "$(ls -A ${MEDIA_SRC} 2>/dev/null)" ]; then
        mkdir -p "${MEDIA_DEST}"
        rsync -avz --quiet "${MEDIA_SRC}/" "${MEDIA_DEST}/"
        
        TOTAL_SIZE=$(du -sh "${MEDIA_DEST}" | cut -f1)
        FILE_COUNT=$(find "${MEDIA_DEST}" -type f | wc -l)
        log_info "媒体文件备份完成: ${FILE_COUNT} 个文件, 共 ${TOTAL_SIZE}"
    else
        log_info "媒体目录为空，跳过备份"
    fi
}

# ===== 3. 备份配置文件 =====
backup_config() {
    log_info "开始备份配置文件..."
    
    CONFIG_DEST="${BACKUP_DIR}/config_${TIMESTAMP}"
    mkdir -p "${CONFIG_DEST}"
    
    # 备份 Nginx 配置
    if [ -f "/etc/nginx/sites-available/${PROJECT_NAME}" ]; then
        cp "/etc/nginx/sites-available/${PROJECT_NAME}" "${CONFIG_DEST}/nginx.conf"
    fi
    
    # 备份 Supervisor 配置
    if [ -f "/etc/supervisor/conf.d/${PROJECT_NAME}.conf" ]; then
        cp "/etc/supervisor/conf.d/${PROJECT_NAME}.conf" "${CONFIG_DEST}/supervisor.conf"
    fi
    
    # 备份 .env（模糊化密码）
    if [ -f "${PROJECT_DIR}/.env" ]; then
        cp "${PROJECT_DIR}/.env" "${CONFIG_DEST}/env.backup"
        sed -i 's/PASSWORD=.*/PASSWORD=***HIDDEN***/' "${CONFIG_DEST}/env.backup"
        sed -i 's/SECRET_KEY=.*/SECRET_KEY=***HIDDEN***/' "${CONFIG_DEST}/env.backup"
    fi
    
    log_info "配置文件备份完成: ${CONFIG_DEST}"
}

# ===== 4. 清理旧备份（保留 RETENTION_DAYS 天） =====
cleanup_old_backups() {
    log_info "清理 ${RETENTION_DAYS} 天前的旧备份..."
    
    # 清理数据库备份
    find "${BACKUP_DIR}/db" -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true
    # 清理媒体备份
    find "${BACKUP_DIR}/media" -mindepth 1 -maxdepth 1 -mtime +${RETENTION_DAYS} -exec rm -rf {} \; 2>/dev/null || true
    # 清理配置备份
    find "${BACKUP_DIR}" -name "config_*" -mtime +${RETENTION_DAYS} -exec rm -rf {} \; 2>/dev/null || true
    
    # 统计
    DB_COUNT=$(find "${BACKUP_DIR}/db" -name "*.sql.gz" | wc -l)
    log_info "当前保留数据库备份: ${DB_COUNT} 份"
}

# ===== 5. 备份报告 =====
generate_report() {
    echo ""
    echo "========================================"
    echo "  备份报告 - ${TIMESTAMP}"
    echo "========================================"
    echo "  数据库备份: ${BACKUP_DIR}/db/"
    du -sh "${BACKUP_DIR}/db/"
    echo "  媒体备份:   ${BACKUP_DIR}/media/"
    du -sh "${BACKUP_DIR}/media/"
    echo "  配置备份:   ${BACKUP_DIR}/"
    echo "  保留天数:   ${RETENTION_DAYS} 天"
    echo "========================================"
    echo ""
}

# ===== 主流程 =====
main() {
    echo ""
    echo "========================================"
    echo "  ${PROJECT_NAME} - 自动备份"
    echo "  $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================"
    echo ""

    backup_database
    backup_media
    backup_config
    cleanup_old_backups
    generate_report

    log_info "全部备份完成！"
}

main "$@"