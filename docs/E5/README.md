# B11 E5–E7 DRAFT 工程

沿用现有仓库，在 `services/draft/` 中加入候选构建验证流程。统一入口为 `python3 scripts/lab_cloud.py`；原有 `make all` 保留为 E4 入口。

参考代码来自 `E5-7.zip` 内学生实验包的 `labs/B-draft/`。学生 ZIP 的 SHA256 为 `4068d3bf98dc8218cc80c6a0f09674d9ed54289b3fcac5cb86eda327fb0cd688`。

已完成的 E5 手工实验见 [运行结果与证据索引](report.md)。

## 开始 E5

在本组云服务器的仓库根目录执行；每次重跑更换输出目录名：

```bash
python3 scripts/lab_cloud.py doctor
python3 scripts/lab_cloud.py build --out work/e5-service-01 --build-timeout 1200
python3 scripts/lab_cloud.py e5 --out work/e5-01 --build-timeout 600
```

E5 应取得 `make: not found` 的完整构建日志，并生成 error-driven、context-driven 两类提示。保存对话模型的原始回复、候选 Dockerfile 和选择理由，再手工复建并按镜像 ID 验证输出 `hello E3`。

## E6、E7 入口

```bash
python3 scripts/lab_cloud.py e6 --candidate work/candidate/error-mirror/Dockerfile --out work/e6-own --build-timeout 600
python3 scripts/verify_e6_b_evidence.py --run-dir work/e6-own/evidence
python3 scripts/lab_cloud.py gate --candidate work/candidate/error-mirror/Dockerfile --out work/e7-01 --build-timeout 600
```

明确选择包内已记录候选时，用 `--replay` 替换 `--candidate ...`。来源见 [候选记录](../../fixtures/ci-candidates/provenance.json)；回放不代表本次生成了新的模型回复。

E7 还需补充自己的测试，并真实完成 CI 失败拒绝合并、修复恢复和最终合并。现有 [workflow](../../.github/workflows/e7-quality-gate.yml) 与 [分支保护配置](../../ci/B-main-protection.json) 提供工程入口；分支保护需要后续在 GitHub 配置并验证。

## 整合说明

- 导入候选约束、两轮构建、同一镜像运行验证、故障场景和 CI。
- 保留 B11 已验证的镜像站与 digest、非交互 Compose 参数、资源自检阈值、完整错误行提取和对应回归测试。
- 教师包有 24 项服务测试；本仓库另保留 1 项 E4 回归测试。
- 报告及候选来源使用 [templates](../../templates/)；验收记录仅保留共同项与 B 组项。
- 真实运行日志写入 `work/`，按阶段整理实际结果。
