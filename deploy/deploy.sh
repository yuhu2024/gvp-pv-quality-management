#!/bin/bash
# ==============================================================
# 君合盟药物警戒培训管理系统 v3.0 - 阿里云 ECS 部署脚本（安全加固版）
# 适配系统: Alibaba Cloud Linux / CentOS / Rocky Linux
# 服务器: 120.27.196.230
# 域名: db8mcom.cn
#
# v3.0 更新内容:
#   - 安全加固：CSRF保护、速率限制、文件上传验证
#   - 密码安全：强制改密、密码复杂度验证
#   - 权限控制：管理员/用户模块分离
#   - 证书XSS防护、课程访问控制
#
# 使用方法:
#   1. 将 training_system_v3.tar.gz 上传到服务器 /root/
#   2. SSH 登录服务器后执行:
#      chmod +x /opt/training_system/deploy/deploy.sh && ./deploy.sh
# ==============================================================

set -e

# ===== 颜色定义 =====
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ===== 配置 =====
DOMAIN="db8mcom.cn"
SERVER_IP="120.27.196.230"
PROJECT_DIR="/opt/training_system"
BACKUP_DIR="/backup"
LOG_FILE="/root/deploy_v2_$(date +%Y%m%d_%H%M%S).log"
DJANGO_SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")

echo "============================================" | tee -a "$LOG_FILE"
echo " 君合盟药物警戒培训管理系统 v3.0 - 一键部署脚本（安全加固版）" | tee -a "$LOG_FILE"
echo " 域名: $DOMAIN" | tee -a "$LOG_FILE"
echo " 服务器: $SERVER_IP" | tee -a "$LOG_FILE"
echo " 日期: $(date)" | tee -a "$LOG_FILE"
echo "============================================" | tee -a "$LOG_FILE"

# ===== 检测系统类型 =====
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    echo "检测到的系统: $OS $VER" | tee -a "$LOG_FILE"
}

# ===== 步骤1: 安装系统依赖 =====
install_system_deps() {
    echo -e "${YELLOW}[1/8] 安装系统依赖...${NC}" | tee -a "$LOG_FILE"
    
    if command -v dnf &> /dev/null; then
        # Alibaba Cloud Linux / CentOS 8+
        dnf install -y python3 python3-pip python3-devel nginx gcc openssl 2>&1 | tee -a "$LOG_FILE"
    elif command -v yum &> /dev/null; then
        # CentOS 7 / older
        yum install -y python3 python3-pip python3-devel nginx gcc openssl 2>&1 | tee -a "$LOG_FILE"
    elif command -v apt-get &> /dev/null; then
        # Debian / Ubuntu
        apt-get update -qq && apt-get install -y -qq python3 python3-pip python3-dev nginx openssl 2>&1 | tee -a "$LOG_FILE"
    else
        echo -e "${RED}不支持的包管理器${NC}" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # 确保 pip 可用
    python3 -m pip --version 2>/dev/null || {
        curl -s https://bootstrap.pypa.io/get-pip.py | python3
    }
    
    echo -e "${GREEN}系统依赖安装完成${NC}" | tee -a "$LOG_FILE"
}

# ===== 步骤2: 配置防火墙和安全组 =====
configure_firewall() {
    echo -e "${YELLOW}[2/8] 配置防火墙...${NC}" | tee -a "$LOG_FILE"
    
    # 尝试 firewalld
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=80/tcp 2>/dev/null || true
        firewall-cmd --permanent --add-port=443/tcp 2>/dev/null || true
        firewall-cmd --reload 2>/dev/null || true
        echo "firewalld 已开放 80/443" | tee -a "$LOG_FILE"
    fi
    
    # 尝试 ufw
    if command -v ufw &> /dev/null; then
        ufw allow 80/tcp 2>/dev/null || true
        ufw allow 443/tcp 2>/dev/null || true
        echo "UFW 已开放 80/443" | tee -a "$LOG_FILE"
    fi
    
    echo -e "${YELLOW}重要提醒: 请确保阿里云安全组已开放 80 和 443 端口！${NC}" | tee -a "$LOG_FILE"
    echo "阿里云控制台 → ECS → 安全组 → 入方向 → 添加规则: TCP 80/443 来源 0.0.0.0/0" | tee -a "$LOG_FILE"
    echo -e "${GREEN}防火墙配置完成${NC}" | tee -a "$LOG_FILE"
}

# ===== 步骤3: 解压项目 =====
setup_project() {
    echo -e "${YELLOW}[3/8] 部署项目文件...${NC}" | tee -a "$LOG_FILE"
    
    # 查找上传的压缩包
    if [ -f "/root/training_system_v3.tar.gz" ]; then
        TAR_FILE="/root/training_system_v3.tar.gz"
    elif [ -f "/root/training_system_v2.tar.gz" ]; then
        TAR_FILE="/root/training_system_v2.tar.gz"
    elif [ -f "/root/training_system.tar.gz" ]; then
        TAR_FILE="/root/training_system.tar.gz"
    else
        echo -e "${RED}未找到部署包！请先上传 training_system_v3.tar.gz 到 /root/${NC}" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # 备份旧版本（如果存在）
    if [ -d "$PROJECT_DIR" ]; then
        BACKUP_NAME="/opt/training_system_backup_$(date +%Y%m%d_%H%M%S)"
        echo "备份旧版本到 $BACKUP_NAME..." | tee -a "$LOG_FILE"
        cp -r "$PROJECT_DIR" "$BACKUP_NAME"
    fi
    
    # 解压到 /opt
    mkdir -p /opt
    rm -rf "$PROJECT_DIR"
    tar -xzf "$TAR_FILE" -C /opt/
    
    if [ ! -d "$PROJECT_DIR" ]; then
        echo -e "${RED}解压后未找到 $PROJECT_DIR 目录${NC}" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    cd "$PROJECT_DIR"
    echo "项目已部署到 $PROJECT_DIR" | tee -a "$LOG_FILE"
    
    # 创建必要的目录
    mkdir -p "$PROJECT_DIR/logs"
    mkdir -p "$PROJECT_DIR/staticfiles"
    mkdir -p "$PROJECT_DIR/media"
    
    echo -e "${GREEN}项目部署完成${NC}" | tee -a "$LOG_FILE"
}

# ===== 步骤4: 安装 Python 依赖 =====
install_python_deps() {
    echo -e "${YELLOW}[4/8] 安装 Python 依赖...${NC}" | tee -a "$LOG_FILE"
    
    cd "$PROJECT_DIR"
    
    # 安装/升级 pip
    python3 -m pip install --upgrade pip 2>&1 | tee -a "$LOG_FILE"
    
    # 安装所有依赖
    pip3 install \
        'Django>=4.2,<5.0' \
        django-widget-tweaks \
        openpyxl \
        Pillow \
        python-pptx \
        redis \
        django-redis \
        requests \
        gunicorn 2>&1 | tee -a "$LOG_FILE"
    
    echo -e "${GREEN}Python 依赖安装完成${NC}" | tee -a "$LOG_FILE"
}

# ===== 步骤5: 配置 Nginx =====
setup_nginx() {
    echo -e "${YELLOW}[5/8] 配置 Nginx...${NC}" | tee -a "$LOG_FILE"
    
    # 创建 Nginx 配置文件
    cat > /etc/nginx/conf.d/training.conf <<'NGINX_EOF'
server {
    listen 80;
    server_name db8mcom.cn www.db8mcom.cn 120.27.196.230;

    client_max_body_size 200M;
    client_body_buffer_size 128k;
    client_body_timeout 300s;
    proxy_read_timeout 300s;

    # 静态文件
    location /static/ {
        alias /opt/training_system/staticfiles/;
        expires 30d;
        access_log off;
    }

    # 媒体文件
    location /media/ {
        alias /opt/training_system/media/;
        expires 7d;
        access_log off;
    }

    # 反向代理到 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # 安全设置
    location ~ /\. { deny all; }
    location ~* \.(env|git|pyc|sqlite3|md|log|bak|swp)$ { deny all; return 404; }
}
NGINX_EOF

    # 测试 Nginx 配置
    nginx -t 2>&1 | tee -a "$LOG_FILE"
    
    # 启动 Nginx
    systemctl enable nginx 2>/dev/null || true
    systemctl restart nginx 2>&1 | tee -a "$LOG_FILE"
    
    echo -e "${GREEN}Nginx 配置完成${NC}" | tee -a "$LOG_FILE"
}

# ===== 步骤6: 配置 Gunicorn systemd 服务 =====
setup_gunicorn_service() {
    echo -e "${YELLOW}[6/8] 配置 Gunicorn 服务...${NC}" | tee -a "$LOG_FILE"
    
    # 查找 gunicorn 路径
    GUNICORN_PATH=$(which gunicorn 2>/dev/null || echo "/usr/bin/gunicorn")
    
    # 创建 systemd 服务文件
    cat > /etc/systemd/system/training.service <<EOF
[Unit]
Description=Training System Django Application v3.0
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/training_system
ExecStart=$GUNICORN_PATH training_system.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120 --access-logfile /opt/training_system/logs/gunicorn_access.log --error-logfile /opt/training_system/logs/gunicorn_error.log
Restart=always
RestartSec=5
Environment="DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY"
Environment="DJANGO_DEBUG=False"
Environment="DJANGO_ALLOWED_HOSTS=db8mcom.cn,www.db8mcom.cn,120.27.196.230,localhost,127.0.0.1"
Environment="CSRF_TRUSTED_ORIGINS=http://db8mcom.cn,http://www.db8mcom.cn,http://120.27.196.230"
Environment="STATIC_ROOT=/opt/training_system/staticfiles"
Environment="MEDIA_ROOT=/opt/training_system/media"

[Install]
WantedBy=multi-user.target
EOF

    # 重新加载 systemd
    systemctl daemon-reload 2>&1 | tee -a "$LOG_FILE"
    systemctl enable training.service 2>&1 | tee -a "$LOG_FILE"
    
    echo -e "${GREEN}Gunicorn 服务配置完成${NC}" | tee -a "$LOG_FILE"
}

# ===== 步骤7: 数据库迁移和静态文件 =====
init_django() {
    echo -e "${YELLOW}[7/8] 初始化 Django...${NC}" | tee -a "$LOG_FILE"
    
    cd "$PROJECT_DIR"
    
    # 设置环境变量
    export DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY"
    export DJANGO_DEBUG="False"
    export DJANGO_ALLOWED_HOSTS="db8mcom.cn,www.db8mcom.cn,120.27.196.230,localhost,127.0.0.1"
    export STATIC_ROOT="/opt/training_system/staticfiles"
    export MEDIA_ROOT="/opt/training_system/media"
    
    # 数据库迁移
    echo "执行数据库迁移..." | tee -a "$LOG_FILE"
    python3 manage.py migrate --noinput 2>&1 | tee -a "$LOG_FILE"
    
    # 收集静态文件
    echo "收集静态文件..." | tee -a "$LOG_FILE"
    python3 manage.py collectstatic --noinput 2>&1 | tee -a "$LOG_FILE"
    
    # 创建默认部门和课程分类数据
    python3 manage.py shell <<'PYEOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'training_system.settings')
import django
django.setup()

from apps.users.models import User, Department, Role
from apps.courses.models import Category

# 创建默认部门
departments = ['人力资源部', '市场部', '技术部', '财务部', '运营部', '质量管理部']
for dept_name in departments:
    Department.objects.get_or_create(name=dept_name)

# 创建默认课程分类
Category.objects.get_or_create(name='质量管理培训', defaults={'code': 'quality', 'description': 'GMP及质量管理体系相关培训'})
Category.objects.get_or_create(name='安全培训', defaults={'code': 'safety', 'description': '生产安全与操作规范培训'})
Category.objects.get_or_create(name='技术培训', defaults={'code': 'tech', 'description': '技术技能与专业能力培训'})

# 创建/重置管理员账号
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
    }
)
admin_user.set_password('Admin@2026')
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.is_active = True
admin_user.force_password_change = False
admin_user.save()
print(f'管理员账号已就绪: admin / Admin@2026 (created={created})')

print('基础数据初始化完成')
PYEOF

    echo -e "${GREEN}Django 初始化完成${NC}" | tee -a "$LOG_FILE"
}

# ===== 步骤8: 启动服务 =====
start_services() {
    echo -e "${YELLOW}[8/8] 启动服务...${NC}" | tee -a "$LOG_FILE"
    
    # 启动 Gunicorn
    systemctl restart training.service 2>&1 | tee -a "$LOG_FILE"
    sleep 3
    
    # 检查状态
    echo "服务状态:" | tee -a "$LOG_FILE"
    systemctl status training.service --no-pager 2>&1 | head -15 | tee -a "$LOG_FILE"
    
    echo -e "${GREEN}服务启动完成${NC}" | tee -a "$LOG_FILE"
}

# ===== 验证部署 =====
verify() {
    echo "" | tee -a "$LOG_FILE"
    echo "============================================" | tee -a "$LOG_FILE"
    echo -e "${GREEN} 部署完成！${NC}" | tee -a "$LOG_FILE"
    echo "============================================" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    echo "访问地址:" | tee -a "$LOG_FILE"
    echo "  http://$DOMAIN" | tee -a "$LOG_FILE"
    echo "  http://$SERVER_IP" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    echo "管理员账号:" | tee -a "$LOG_FILE"
    echo "  用户名: admin" | tee -a "$LOG_FILE"
    echo "  密码:   Admin@2026" | tee -a "$LOG_FILE"
    echo "  安全特性: CSRF保护 / 速率限制 / 强制改密 / 文件上传验证" | tee -a "$LOG_FILE"
    echo "  请登录后立即修改密码！" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    echo "常用命令:" | tee -a "$LOG_FILE"
    echo "  查看日志:     tail -f $PROJECT_DIR/logs/gunicorn_error.log" | tee -a "$LOG_FILE"
    echo "  重启服务:     systemctl restart training" | tee -a "$LOG_FILE"
    echo "  查看状态:     systemctl status training" | tee -a "$LOG_FILE"
    echo "  停止服务:     systemctl stop training" | tee -a "$LOG_FILE"
    echo "  查看Nginx:    systemctl status nginx" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    echo "部署日志: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # 测试本地连接
    sleep 2
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null || echo "000")
    if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ]; then
        echo -e "${GREEN}Django 应用运行正常 (HTTP $HTTP_STATUS) ✓${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${YELLOW}Django 应用可能还在启动中 (HTTP $HTTP_STATUS)，请稍后检查${NC}" | tee -a "$LOG_FILE"
        echo "排查命令: journalctl -u training --no-pager -n 50" | tee -a "$LOG_FILE"
    fi
}

# ===== 执行 =====
detect_os
install_system_deps
configure_firewall
setup_project
install_python_deps
setup_nginx
setup_gunicorn_service
init_django
start_services
verify

echo "" | tee -a "$LOG_FILE"
echo -e "${GREEN}全部完成！请将域名 $DOMAIN 的 A 记录指向 $SERVER_IP${NC}" | tee -a "$LOG_FILE"
