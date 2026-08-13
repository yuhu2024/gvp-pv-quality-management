#!/bin/bash
# ============================================================
# 君合盟药物警戒培训管理系统 v4.0 - GitHub 一键部署脚本
# 在阿里云 ECS 服务器上执行
#
# 使用方法:
#   curl -sL https://raw.githubusercontent.com/yuhu2024/gvp-pv-quality-management/main/deploy_from_github.sh | bash
# ============================================================
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
PROJECT_DIR="/opt/training_system"
GIT_URL="https://github.com/yuhu2024/gvp-pv-quality-management.git"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN} 君合盟药物警戒培训管理系统 v4.0${NC}"
echo -e "${GREEN} GitHub 一键部署${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. 停止旧服务
echo -e "\n${YELLOW}[1/7] 停止旧服务...${NC}"
systemctl stop training.service 2>/dev/null || true
echo -e "${GREEN}✓ 旧服务已停止${NC}"

# 2. 备份
echo -e "\n${YELLOW}[2/7] 备份现有系统...${NC}"
if [ -d "$PROJECT_DIR" ]; then
    BACKUP_DIR="/opt/training_system_backup_$(date +%Y%m%d_%H%M%S)"
    cp -r "$PROJECT_DIR" "$BACKUP_DIR" 2>/dev/null || true
    cp "$PROJECT_DIR/db.sqlite3" /tmp/db_backup.sqlite3 2>/dev/null || true
    cp -r "$PROJECT_DIR/media" /tmp/media_backup 2>/dev/null || true
    cp "$PROJECT_DIR/.env" /tmp/env_backup 2>/dev/null || true
    echo -e "${GREEN}✓ 已备份到 $BACKUP_DIR${NC}"
else
    echo "系统目录不存在，跳过备份"
fi

# 3. 安装依赖
echo -e "\n${YELLOW}[3/7] 安装系统依赖...${NC}"
dnf install -y python3 python3-pip nginx git 2>/dev/null || yum install -y python3 python3-pip nginx git 2>/dev/null || true
echo -e "${GREEN}✓ 系统依赖就绪${NC}"

# 4. 克隆代码
echo -e "\n${YELLOW}[4/7] 从 GitHub 克隆代码...${NC}"
rm -rf "$PROJECT_DIR"
git clone --depth 1 "$GIT_URL" "$PROJECT_DIR" 2>&1 | tail -3
echo -e "${GREEN}✓ 代码克隆完成${NC}"

cp /tmp/db_backup.sqlite3 "$PROJECT_DIR/db.sqlite3" 2>/dev/null || true
cp -r /tmp/media_backup "$PROJECT_DIR/media" 2>/dev/null || true
mkdir -p "$PROJECT_DIR/logs" "$PROJECT_DIR/staticfiles" "$PROJECT_DIR/media"

# 5. 安装 Python 依赖
echo -e "\n${YELLOW}[5/7] 安装 Python 依赖...${NC}"
pip3 install --quiet \
    'Django>=4.2,<5.0' \
    django-widget-tweaks \
    openpyxl Pillow python-pptx \
    requests qrcode gunicorn 2>&1 | tail -3
echo -e "${GREEN}✓ Python 依赖安装完成${NC}"

# 6. 配置环境、迁移、收集静态文件、部署数据
echo -e "\n${YELLOW}[6/7] 配置环境并迁移数据库...${NC}"
cd "$PROJECT_DIR"

if [ -f /tmp/env_backup ]; then
    cp /tmp/env_backup "$PROJECT_DIR/.env"
    if ! grep -q "SYSTEM_NAME" "$PROJECT_DIR/.env"; then
        echo 'SYSTEM_NAME="君合盟药物警戒培训管理系统"' >> "$PROJECT_DIR/.env"
        echo 'SYSTEM_SHORT_NAME="君合盟PV培训系统"' >> "$PROJECT_DIR/.env"
    fi
    if ! grep -q "db8mcom.cn" "$PROJECT_DIR/.env" 2>/dev/null; then
        echo 'DJANGO_ALLOWED_HOSTS="120.27.196.230,db8mcom.cn,www.db8mcom.cn,localhost,127.0.0.1"' >> "$PROJECT_DIR/.env"
        echo 'CSRF_TRUSTED_ORIGINS="http://120.27.196.230,http://db8mcom.cn,http://www.db8mcom.cn"' >> "$PROJECT_DIR/.env"
    fi
else
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    cat > "$PROJECT_DIR/.env" << EOF
DJANGO_SECRET_KEY="${SECRET_KEY}"
DJANGO_DEBUG="False"
DJANGO_ALLOWED_HOSTS="120.27.196.230,db8mcom.cn,www.db8mcom.cn,localhost,127.0.0.1"
SYSTEM_NAME="君合盟药物警戒培训管理系统"
SYSTEM_SHORT_NAME="君合盟PV培训系统"
CSRF_TRUSTED_ORIGINS="http://120.27.196.230,http://db8mcom.cn,http://www.db8mcom.cn"
EOF
fi
chmod 600 "$PROJECT_DIR/.env"

export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)

python3 manage.py migrate --noinput 2>&1 | tail -5
python3 manage.py collectstatic --noinput 2>&1 | tail -3

echo -e "\n${YELLOW}  部署药物警戒培训数据...${NC}"
python3 manage.py shell << 'PYEOF'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'training_system.settings')
django.setup()

from apps.users.models import User, Department
from apps.courses.models import Category, Course
from apps.plans.models import TrainingPlan
from apps.exams.models import Exam
from apps.config.models import SystemConfig, ScoreWeightConfig
from django.utils import timezone
from datetime import date

admin, _ = User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True, 'email': 'admin@jhmpharm.com'})
if not admin.has_usable_password():
    admin.set_password('admin123')
    admin.save()
admin.force_password_change = False
admin.save()
print('  ✓ 管理员账号: admin / admin123')

for d in [{'name':'药物警戒部','code':'PV'},{'name':'质量保证部','code':'QA'},{'name':'人力资源部','code':'HR'},{'name':'临床医学部','code':'CMD'},{'name':'药品安全委员会','code':'DSC'}]:
    Department.objects.get_or_create(code=d['code'], defaults={**d, 'description':f'负责{d["name"]}相关工作'})
print('  ✓ 5个部门已创建')

cat_map = {}
for c in [{'name':'法规与指南','code':'REG','order':1},{'name':'基础知识','code':'BASIC','order':2},{'name':'体系文件','code':'SYS','order':3},{'name':'其他','code':'OTHER','order':4}]:
    cat, _ = Category.objects.get_or_create(code=c['code'], defaults=c)
    cat_map[c['code']] = cat
print('  ✓ 4个课程分类已创建')

courses = [
    ('药物警戒质量管理规范（GVP）培训','REG','《药物警戒质量管理规范》（2021年）法规解读'),
    ('药品管理法与药物警戒法规培训','REG','《药品管理法》药物警戒相关条款解读'),
    ('药物警戒基础知识培训','BASIC','PV常见名词及定义，ADR基本概念'),
    ('药品安全委员会管理规程培训','SYS','《药品安全委员会管理规程》宣贯'),
    ('药物警戒培训管理规程培训','SYS','JHM-TPV53-1005培训管理规程宣贯'),
    ('药品不良反应收集和报告培训','BASIC','ADR收集渠道、报告时限、填写规范'),
    ('产品安全性信息培训','OTHER','产品安全性信息、适应症基础知识'),
    ('药物警戒体系文件培训','SYS','药物警戒法律法规和技术指导原则'),
]
course_map = {}
for title, cat_code, desc in courses:
    c, _ = Course.objects.get_or_create(title=title, defaults={'category':cat_map.get(cat_code),'description':desc,'creator':admin,'status':'published','published_at':timezone.now()})
    course_map[title] = c
print('  ✓ 8门培训课程已创建')

for title, ct in [('药物警戒质量管理规范（GVP）考核','药物警戒质量管理规范（GVP）培训'),('药品管理法与药物警戒法规考核','药品管理法与药物警戒法规培训'),('药物警戒基础知识考核','药物警戒基础知识培训'),('药物警戒培训管理规程考核','药物警戒培训管理规程培训'),('药物警戒体系文件考核','药物警戒体系文件培训')]:
    Exam.objects.get_or_create(title=title, defaults={'course':course_map.get(ct),'duration':60,'total_score':100,'pass_score':90,'is_published':True,'allow_retake':True,'max_attempts':0,'require_pass':True,'created_by':admin})
print('  ✓ 5场培训考试已创建（合格线90分）')

yr = date.today().year
plan, _ = TrainingPlan.objects.get_or_create(title=f'{yr}年度药物警戒培训计划', defaults={'description':'依据JHM-TPV53-1005《药物警戒培训管理规程》制定','start_date':date(yr, 1, 1),'end_date':date(yr, 12, 31),'status':'in_progress','is_mandatory':True,'require_exam_pass':True,'allow_retake':True,'max_attempts':0,'creator':admin})
for c in course_map.values():
    plan.courses.add(c)
for e in Exam.objects.filter(title__in=['药物警戒质量管理规范（GVP）考核','药品管理法与药物警戒法规考核','药物警戒基础知识考核','药物警戒培训管理规程考核','药物警戒体系文件考核']):
    plan.exams.add(e)
print('  ✓ 年度培训计划已创建')

for key, val, vtype, label in [('pv_training_pass_rate','98','integer','培训合格率要求(%)'),('pv_exam_pass_score','90','integer','笔试合格分数线'),('pv_training_plan_form_code','JHM-81-(TPV53-1005)-02','string','年度培训计划表编号'),('pv_training_record_form_code','JHM-81-(TPV53-1005)-03','string','培训记录表编号'),('pv_training_summary_form_code','JHM-81-(TPV53-1005)-04','string','培训汇总表编号'),('pv_training_adjustment_form_code','JHM-81-(TPV53-1005)-05','string','培训计划调整申请表编号')]:
    SystemConfig.objects.update_or_create(key=key, defaults={'group':'training','value':val,'value_type':vtype,'label':label})
print('  ✓ 培训配置参数已设置')

for course in course_map.values():
    ScoreWeightConfig.objects.get_or_create(course=course, defaults={'video_weight':20,'material_weight':30,'exam_weight':50,'pass_score':90})
print('  ✓ 成绩权重已配置')
print('  ✓ 药物警戒培训数据部署完成！')
PYEOF

echo -e "${GREEN}✓ 数据库迁移和数据部署完成${NC}"

# 7. 配置服务并启动
echo -e "\n${YELLOW}[7/7] 配置系统服务并启动...${NC}"

GUNICORN_PATH=$(which gunicorn 2>/dev/null || echo "/usr/local/bin/gunicorn")

cat > /etc/systemd/system/training.service << EOF
[Unit]
Description=君合盟药物警戒培训管理系统
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$GUNICORN_PATH --workers 3 --bind 127.0.0.1:8000 --timeout 120 --access-logfile $PROJECT_DIR/logs/gunicorn_access.log --error-logfile $PROJECT_DIR/logs/gunicorn_error.log training_system.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl restart training
systemctl enable training
sleep 3
echo -e "${GREEN}✓ Gunicorn 服务已启动${NC}"

cat > /etc/nginx/conf.d/training.conf << 'NGINX_EOF'
server {
    listen 80;
    server_name 120.27.196.230 db8mcom.cn www.db8mcom.cn;
    client_max_body_size 200M;
    location /static/ { alias /opt/training_system/staticfiles/; expires 30d; }
    location /media/ { alias /opt/training_system/media/; expires 7d; }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
    location ~ /\. { deny all; }
    location ~* \.(env|git|pyc|sqlite3|log|bak)$ { deny all; return 404; }
}
NGINX_EOF

rm -f /etc/nginx/conf.d/default.conf 2>/dev/null || true
nginx -t 2>&1
systemctl restart nginx
systemctl enable nginx
echo -e "${GREEN}✓ Nginx 已配置并启动${NC}"

sleep 3
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login/ 2>/dev/null || echo "000")
NGINX_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/ 2>/dev/null || echo "000")

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN} 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "访问地址: http://120.27.196.230"
echo "管理员:   admin / admin123"
echo ""
echo "v4.0 更新内容:"
echo "  ✓ 二维码签到功能（微信扫码+手机手写签名）"
echo "  ✓ 培训矩阵模块（按部门配置，个人查看进度）"
echo "  ✓ 系统名称改为「君合盟药物警戒培训管理系统」"
echo "  ✓ 8门药物警戒培训课程"
echo "  ✓ 5场培训考试（合格线90分）"
echo "  ✓ 年度药物警戒培训计划"
echo "  ✓ 药物警戒培训配置参数"
echo ""
echo "服务状态:"
echo "  Gunicorn (8000): $HTTP_STATUS"
echo "  Nginx (80):      $NGINX_STATUS"
if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ]; then
    echo -e "${GREEN}✓ 系统运行正常${NC}"
else
    echo -e "${YELLOW}⚠ 系统可能还在启动中，请稍后检查${NC}"
    echo "排查命令: journalctl -u training --no-pager -n 30"
fi