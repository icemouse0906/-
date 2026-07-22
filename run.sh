set -e

echo "== 合并镜像分卷（若存在） =="
if ls docker-images/ultimate_stack.tar.gz.part_* 1>/dev/null 2>&1; then
  cat docker-images/ultimate_stack.tar.gz.part_* > docker-images/ultimate_stack.tar.gz
fi

echo "== 导入镜像 =="
gunzip -c docker-images/ultimate_stack.tar.gz | docker load

echo "== 启动服务 =="
docker compose up -d

echo "== 完成！访问 http://<本机IP>:5005/ 检查健康状态 =="
