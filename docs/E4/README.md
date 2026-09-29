# B11 E4 准备与验收

E2 已完成，E3 正在推进。本页依据教师提供的 E4 课件及 B 组全流程命令手册整理，只记录准备方案，不冒充真实运行结果。

## 本次目标

将 B 组 DRAFT 服务骨架做成可重复工程环境：同一源码 SHA，在组员各自克隆中执行 `make all`，完成环境自检、构建、单元测试、冒烟测试及密钥扫描，并留下证据。

E4 不要求实现完整 DRAFT 自动生成与修复算法，也不要求同时搭建 MDFixer。模板中的 CLI、测试和 E3 小样例用于证明服务环境可用。

## 当前准备状态

- 已有：E4 B 组命令手册、E4 课件、E3 课件，以及本组 E2 契约材料。
- 已导入：实验包中的 B-draft 模板和服务器初始化脚本；原始模板说明见 [模板 README](template_README.md)，来源与文件摘要见 [导入清单](template_manifest.json)。初始化脚本尚未执行。
- 尚未验证：服务器登录、Docker 可用性、模板构建、真实冒烟和组员重跑。
- 下一步：完成组内提交与服务器准备，在各自克隆中运行 make doctor 和 make all。

## 仓库整合方案

保留现有单仓库与 E2 成果，采用课件规定的 `services/draft/` 结构。以下是目标布局，不表示文件已全部存在：

```text
devops/
├── README.md
├── docs/
│   ├── E2/
│   ├── E3/
│   └── E4/
├── contract/                 # 现有 Schema 和接口样例
├── services/
│   └── draft/                # 教师 B-draft 模板中的 DRAFT 服务
├── fixtures/
│   └── draft/                # 冒烟所需源码和故意失败的 Dockerfile
├── scripts/                  # 模板自检、扫描等脚本
├── compose.yaml
├── Makefile
├── requirements-dev.in
├── requirements-dev.lock
├── .env.example
├── .gitignore
├── .dockerignore
├── tests/                    # 已有契约校验，区别于服务单测
└── work/                     # 真实运行证据，不进入 Git 或镜像
```

整合时先比较同名文件，尤其 README、Makefile 和忽略规则；不将模板直接覆盖到现有项目。保留 contract/ 和 docs/E2/。检查模板的构建上下文及 Makefile 路径，沿用根目录 `make all` 入口。教师模板单测与 E2 契约校验分别报告，不把先前 29 项文件校验当作 E4 服务测试结果。

## 准备任务

| 顺序 | 工作 | 完成条件 |
|---|---|---|
| 1 | 获取并核对 B-draft 原始模板 | 能检查 Dockerfile、Compose、Makefile、锁文件、自检/扫描脚本及 fixtures |
| 2 | 检查本组服务器 | 确认系统、架构、Docker Engine、Compose、Buildx 和实际网络可达性；已有可用 Docker 不重复安装 |
| 3 | 整合模板到本组仓库 | 保留 E2 内容、记录模板来源；确认 .env、work/、缓存被忽略，依赖和基础镜像固定 |
| 4 | 发布组内统一模板版本 | 完成必要的组级提交与推送，其他成员能克隆相同 SHA；不改变共享全局 Git 身份 |
| 5 | 每位成员独立运行 | 在自己的学号目录克隆，设置本仓库 Git 身份，make doctor 通过后执行 make all |
| 6 | 检查扫描器能发现假密钥 | 只在个人克隆中使用教师规定的假 Key；扫描应拒绝，删除后应通过 |
| 7 | 比较两名成员结果 | 完整 SHA 相同，工具版本与测试/冒烟结论一致；差异有解释 |

实际成员学号、服务器地址、账号和访问方式以教师发放的信息为准。密码、真实 API Key 和 Token 不写入文档、命令记录或仓库。E4 模板测试无需真实 LLM Key。

## 运行流程

拿到模板并整合后，每名成员在服务器自己的克隆根目录执行：

```bash
git rev-parse HEAD
git status --short
make doctor
make all
```

执行前按教师手册使用 `git config --local` 配置本人的学号与邮箱。两名成员分别克隆运行，不共享一个工作树；首次下载和构建按顺序进行，避免同时重复构建。

`make all` 顺序为 `doctor → build → test → smoke → scan`。完整运行的证据必须来自同一次成功运行目录，不把单独重跑 scan 产生的新目录误认成 make all 的结果。

## E4 特有的检查点

- B 组容器只安装 Docker 客户端，通过宿主机 docker.sock 使用宿主机引擎；不是在容器内另装一套 Docker Engine。
- Makefile 应注入 docker.sock 的组号，使默认 app 用户能执行冒烟；不能用 root 下的 make shell 代替这个检查。
- 基础 Python 镜像与 Docker CLI 镜像按 digest 固定；Python 依赖锁文件带哈希，系统工具导出实际版本。
- 服务 Compose 的 CPU/内存限制不等于宿主机 Docker 构建的资源限制。遵循课程约束，不清理他人的镜像或缓存，不开放 Docker API 端口。
- 故意失败的 Dockerfile 缺少 make，预期构建非零退出；smoke.json 的 passed=true 表示成功识别预期失败，不表示目标镜像成功构建。
- 检查 make_error_line 包含 `make: not found`，不能只凭非零退出码通过：网络或权限错误不属于预期样例失败。

## 证据清单

| 材料 | 验收内容 |
|---|---|
| 源码 SHA 与仓库地址 | 完整 git rev-parse HEAD 和本组远程地址 |
| env.json | problems 为空，Git 本地身份属于当前学生；资源 warnings 与 problems 分开解释 |
| build.log、image.json | 服务镜像真实构建成功，包含镜像来源及身份 |
| toolchain.lock、requirements-dev.lock | 实际工具版本与按哈希固定的 Python 依赖 |
| test.log | 原始模板手册预期 4 passed；以所用模板版本的实际测试集为准 |
| smoke.json | Docker Server 可达、目标构建非零退出、关键错误为 make: not found、passed=true |
| secret-scan.txt | 无密钥问题；假 Key 的拒绝与删除后通过另留记录 |
| 组员重跑对照 | 至少两名组员各自目录、相同源码 SHA、成功运行目录及结论比较 |

镜像 ID、耗时和日志行数可能不同；不能据此直接认定不可重复。重点比较固定依赖、实际工具版本和测试结论。

E4 普通成员不要求个人提交、推送或组长合并；所记录 SHA 是运行的小组模板版本。work/ 默认不进 Git，按课程提交要求提供真实证据。

## 与 E3、E5 的关系

E3 的 B 组内容包括 DRAFT 失败/参考成功构建样本，以及 MDFixer 固定 MD 和补丁验证。E4 仅取需要的源码做冒烟，不把 E3 的历史输出复制为本次运行证据。

E4 smoke.json 的日志末尾与关键行不代替 E5 完整原始日志。E5 需在同一服务环境中重新执行并保存完整输出和退出码。

## 依据

- 教师《E4 B 组（DRAFT）全流程命令手册》：模板获取、逐人克隆、一键运行、扫描与重跑。
- 《E4 可重复工程环境》课件：第 4、7—20、23 页。
- 《E3 并行测试基线》课件：B 组 DRAFT 样本和 MDFixer 固定输入部分。

源材料位于本机 `~/devops_resources/`。本文不复制教师凭据或同学名单，也不包含运行日期标注。
