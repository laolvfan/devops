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

目前已记录统一提交路径，尚未连接服务器或写入 `/root/submit`。第一阶段本地准备日志保存在仓库 `docs/E7/preparation-evidence/`，正式 E7 gate 和 CI 的后续结果单独归档。
