# B11 DevOps 课程项目

B11 负责 B 轨道的两个组件：

- **DRAFT**：为 C/Make 项目自动生成可构建的 Dockerfile，经过多轮构建与修正得到可用环境。
- **MDFixer**：读取 MD（Missing Dependency）报告，为 Makefile 补全缺失的头文件依赖，并通过重新构建验证补丁。只处理 MISSING，REDUNDANT 不处理。

A11 负责 A 轨道的 BuildChecker（全量检测）与 EChecker（增量检测）。E12 完整链路如下：

```text
DRAFT（B11） → BuildChecker 全量检测（A11） → EChecker 增量检测（A11） → MDFixer 修复（B11） → 重新构建/检测
   构建环境           基线提交依赖图                 目标提交 MD/RD 报告           补丁与验证结果
```

各环节使用上一环节的实际输出作为输入，并通过 `job_id`/`trace_id`、报告中的 `commit` 和产物 SHA256 进行衔接与核对。

## 项目结构

```text
devops/
├── README.md
├── Makefile、compose.yaml        # E4 可重复环境入口（make all = doctor+build+test+smoke+scan）
├── run_lab.py                    # E8–E10 统一入口（build / e8 / e9 / e10，--track A|B）
├── requirements-dev.in/.lock     # 开发依赖及带哈希的锁文件
├── .github/workflows/            # CI：e7-quality-gate.yml、e8e10.yml
│
├── contract/                     # A11/B11 共用接口契约
│   ├── schemas/                  #   task / md-report / draft-iterations 的 JSON Schema
│   └── examples/                 #   draft、full_check、incremental_check、repair 请求与响应样例
│
├── services/draft/               # DRAFT 服务（教师 B-draft 模板及本组实现、测试）
├── labs/e8e10/                   # E8–E10 实验代码（lab.py）与运行环境
├── fixtures/                     # 测试输入：draft/ 失败与参考 Dockerfile，ci-candidates/ CI 候选
├── scripts/                      # 运行与检查脚本
│   ├── lab_cloud.py              #   E5–E7 统一运行入口
│   ├── doctor.py、secret_scan.py #   环境自检、密钥扫描
│   ├── run_e7_b_gate.py          #   E7 B 轨道质量门禁
│   └── e3/                       #   E3 DRAFT / MDFixer 验证脚本
├── tests/                        # 契约 Schema、样例、响应格式及 E7 门禁测试
├── ci/                           # main 分支保护配置与 CI 拒绝恢复演示
├── setup/bootstrap_ubuntu.sh     # 服务器初始化脚本
├── templates/                    # 实验报告、验收记录、候选来源记录模板
├── work/                         # 已归档的运行证据（其余运行记录不入库）
├── paper/                        # 参考论文（DRAFT、MDFixer 原文）
│
└── docs/
    ├── E2/                       # 需求、接口契约、MD 报告格式、产物交接、ADR
    ├── E3/                       # 并行测试基线
    ├── E4/                       # 可重复工程环境
    ├── E5/  E6/  E7/             # DRAFT 工程、自动构建、CI 质量门禁
    └── students/<学号>/e8-e10/   # 个人报告、ADR、AI 使用记录与证据索引
```

## 接口契约

联调时以下列文件为准：

| 内容 | 位置 |
|---|---|
| 任务接口、状态与错误 | [docs/E2/interface_contract.md](docs/E2/interface_contract.md) |
| MD/RD 报告格式 | [docs/E2/md_report.md](docs/E2/md_report.md) |
| 产物 URI 与下载方式 | [docs/E2/artifact_handoff.md](docs/E2/artifact_handoff.md) |
| HTTP 响应格式 | [docs/E2/response_formats.md](docs/E2/response_formats.md) |
| 设计决策（ADR） | [docs/E2/decisions/](docs/E2/decisions/README.md) |
| JSON Schema 与样例 | [contract/schemas/](contract/schemas/README.md)、[contract/examples/](contract/examples/README.md) |

## 阶段进度

| 阶段 | 内容 | 文档 |
|---|---|---|
| E2 | 需求与接口契约 | [docs/E2](docs/E2/interface_contract.md) |
| E3 | DRAFT 失败与参考成功验证；MDFixer 四种补丁（Target/Macro/Hybrid/Implicit）及拒绝恢复 | [docs/E3](docs/E3/README.md) |
| E4 | 导入教师 B-draft 模板，三位成员完成构建、测试、冒烟和密钥检查，并做同 SHA 重跑对照 | [docs/E4](docs/E4/README.md) |
| E5–E7 | 真实项目 DRAFT 工程、自动构建、故障场景与 CI 拒绝恢复 | [E5](docs/E5/README.md)、[E6](docs/E6/README.md)、[E7](docs/E7/report.md) |
| E8–E10 | 个人实验与测试扩展，组内合并为统一版本 | [docs/students](docs/students/) |
| E11–E12 | 轨道内集成与 A11/B11 接口联调 | 进行中，见 `e11-e12-integration` 分支 |
