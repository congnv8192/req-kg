#!/bin/bash

# 个性化设置API启动脚本

# 设置脚本在遇到错误时退出
set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}🚀 启动个性化设置API服务...${NC}"

# 检查Python环境
echo -e "${YELLOW}检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到Python 3，请安装Python 3.8或更高版本${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python版本: $PYTHON_VERSION${NC}"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source venv/bin/activate

# 升级pip
echo -e "${YELLOW}升级pip...${NC}"
pip install --upgrade pip

# 安装依赖
echo -e "${YELLOW}安装项目依赖...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${RED}❌ 错误: 未找到requirements.txt文件${NC}"
    exit 1
fi

# 检查端口是否被占用
PORT=8082
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  警告: 端口$PORT已被占用，尝试停止占用进程...${NC}"
    PID=$(lsof -ti:$PORT)
    if [ ! -z "$PID" ]; then
        echo -e "${YELLOW}停止进程PID: $PID${NC}"
        kill -9 $PID 2>/dev/null || true
        sleep 2
    fi
fi

# 创建必要的目录
echo -e "${YELLOW}创建必要目录...${NC}"
mkdir -p logs
mkdir -p data

# 启动服务
echo -e "${GREEN}启动API服务...${NC}"
echo -e "${BLUE}服务地址: http://localhost:$PORT${NC}"
echo -e "${BLUE}API文档: http://localhost:$PORT/docs${NC}"
echo -e "${BLUE}健康检查: http://localhost:$PORT/health${NC}"

# 使用uvicorn启动服务，支持热重载
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --reload \
    --log-level info \
    --access-log \
    --workers 1

# 注意：脚本会在服务启动后阻塞，直到Ctrl+C停止服务
