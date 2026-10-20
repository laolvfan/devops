# 服务器统一提交归档

小组最终提交目录确定为 `/root/submit`。为便于三人汇总，建议按阶段保存：

```text
/root/submit/
├── E5/                         # P1 整理
├── E6/                         # P2 整理
└── E7/                         # 本阶段负责人整理
    ├── README.md               # 版本、运行结果与证据索引
    ├── source-code.tar.gz      # 交付版本的跟踪代码
    ├── source-commit.txt
    ├── reports/                # E7 报告、场景表、交接与验收表
    ├── evidence/
    │   ├── local/              # 正式单元测试、五场景和完整 gate
    │   └── ci/
    │       ├── normal/
    │       ├── rejection/
    │       └── recovery/
    └── merge/                  # 分支保护、合并拒绝与最终合并记录
```

`/root/submit` 是用户确定的根目录；E5/E6/E7 子目录是协作整理约定，可与其他同学统一调整。每位同学维护自己的阶段目录，保留他人的产物。

## E7 入库条件

1. 正式版本的服务测试和五个真实场景均通过，gate-result.json、results.csv 与原始日志齐全。
2. 保存 CI 正常、失败、恢复的运行 URL 与下载 artifact，结果能够对应提交和镜像 ID。
3. 保存 main 保护配置、普通合并拒绝日志，以及同一 PR 最终合并记录。
4. 报告分别列出教师参考、P1 的实际候选及人工换源调整、小组的测试与代码修改。
5. 验收表的 PASS 项均有证据；未执行项如实填写 PENDING。

## 归档方式

在服务器上按实际仓库和证据路径整理。代码快照可用 `git archive` 导出跟踪文件，版本用 `git rev-parse HEAD` 保存；正式 gate 输出从相应 `work/` 新目录复制到 `E7/evidence/local/`。CI artifact 在 14 天保留期内下载后分别放入三个 CI 子目录。

只归档交付所需源码、报告与证据；本机虚拟环境、Git 登录配置和密钥文件不纳入提交。复制后核对文件清单，传输的候选或压缩包按需要核对一次完整性。

正式服务器 gate 已完成，三阶段 CI 的原始 ZIP 和元数据已保存在 `docs/E7/ci-evidence/`。PR #3 合并后，按 server-commands.md 取得准确版本并执行 `bash scripts/submit_e7.sh`，脚本会核对合并状态、服务器原始 gate、CI 结论与 ZIP 完整性后完成整理。

恢复执行的 SHA 早于最后的报告提交。脚本校验它是最终 PR head 的祖先，并核对服务、fixture、候选、门禁、依赖与 CI workflow 的运行输入没有变化。提交目录中的 CSV、交接 JSON 和报告在核对实际合并结果后补齐最终状态。以 `ARCHIVE_COMPLETE=/root/submit/E7` 与进程退出码 0 确认归档完成。
