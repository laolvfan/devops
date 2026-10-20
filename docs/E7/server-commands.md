# E7 服务器操作命令

在已登录课程云服务器的终端执行。每一段完成后检查退出码；失败时保留结果目录，把报错和命令输出交给协作者核对。

## 1. 自检

```bash
whoami
uname -srmo
docker version
docker compose version
docker buildx version
df -h / /root
free -h
```

应能看到 Docker Client 和 Server。后续目录位于 /root，需使用有权限的课程账号。P1 的实验记录是 Ubuntu 22.04.5、2 CPU、约 3.54 GiB 内存，共享服务器上完整 Docker 门禁错峰运行。

## 2. 独立检出 E7

自检通过后，创建一个新的独立目录。命令中的姓名信息用本人学号和提交邮箱填写。

```bash
read -r -p "你的学号: " sid
read -r -p "你的 Git 提交邮箱: " student_mail
repo_dir=$(mktemp -d /root/devops-e7.XXXXXX)
git clone --branch feat/e7-quality-gate --single-branch https://github.com/laolvfan/devops.git "$repo_dir"
cd "$repo_dir"
git config --local user.name "$sid"
git config --local user.email "$student_mail"
git log -1 --oneline
python3 scripts/lab_cloud.py doctor
echo "DOCTOR_EXIT_CODE=$?"
```

保留终端中的 repo_dir、sid 变量；重新登录后先进入对应目录并重新设置 sid。公共仓库克隆无需在命令中填写 Token。

## 3. 构建服务并运行测试

```bash
image="e7-draft:$sid"
stamp=$(date +%Y%m%d-%H%M%S)
python3 -m unittest discover -s tests/e7 -v
python3 scripts/lab_cloud.py build --image "$image" --out "work/e7-build-$stamp" --build-timeout 1200
echo "BUILD_AND_TEST_EXIT_CODE=$?"
```

当前基础版本预期为 6 项独立判定测试，以及 26 项服务测试通过。构建及服务测试退出码应为 0；若上游加入测试，按实际数量记录。

## 4. 五场景门禁

```bash
gate_dir="work/e7-gate-$(date +%Y%m%d-%H%M%S)"
python3 scripts/lab_cloud.py gate \
  --image "$image" \
  --candidate work/candidate/error-mirror/Dockerfile \
  --out "$gate_dir" --build-timeout 600
gate_code=$?
echo "E7_GATE_EXIT_CODE=$gate_code"
cat "$gate_dir/gate/gate-result.json"
cat "$gate_dir/gate/results.csv"
```

正式通过条件：整体退出码 0，服务测试和五场景共六项 passed=true。预期失败场景正确识别错误时可通过；运行超时要求次轮构建成功且运行容器已经清理。原始结果均保存在 gate_dir 下，重跑使用新目录。

## 5. 放入统一提交目录

完整门禁及 CI 演示通过、PR #3 合并后执行，检出协作者提供的最终合并提交。脚本只整理 E7 目录，保留其他同学的 E5/E6 目录。

```bash
cd /root/devops-e7.d149Jj
git -c http.version=HTTP/1.1 fetch origin main
git switch --detach FETCH_HEAD
bash scripts/submit_e7.sh
echo "ARCHIVE_EXIT_CODE=$?"
```

预期出现 `ARCHIVE_COMPLETE=/root/submit/E7`，退出码为 0。若 main 已有后续他人的提交，脚本会要求切换到 PR #3 的准确合并 SHA 后再归档。源码包来自合并提交的跟踪文件，虚拟环境和未跟踪登录信息不包含在 git archive 中。
