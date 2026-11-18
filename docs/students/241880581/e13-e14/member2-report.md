# E13–E14 成员二个人记录

本轮我负责成员二任务，完成 H1-jsmn、H2-inih 和 H3-tiny-AES 三个项目的 DRAFT、修复和复检，验证均接受。E11–E12 测试 24 项、E13 交接测试 3 项通过。

cJSON 使用 A 组提供的当次 fixed-md 报告，包校验通过，报告 SHA256 为 `3b77016dd7a243c11ed7e22b07f4b8c7a1a848727ce358685403576329136b72`。B 侧修复任务成功，补丁为 `cJSON_Utils.o` 增加 `cJSON.h`，验证接受，复检无 MISSING。

C4 超时请求返回 `DRAFT_FAILED/TIMED_OUT`，未发现残留构建进程；C5 无效补丁被拒绝，target 项目的 HEAD 和 Makefile 哈希不变，`rollback=true`；C6 假密钥注入时扫描命中，清理后通过；C7 篡改报告哈希被拒绝，正确请求随后成功；C8 相同 key 和请求返回 202 与同一 job，不同请求返回 409。cJSON 相关运行日志最终扫描 25 个文本文件，0 hits、0 errors。

E14 固定样例五阶段成功。超时任务失败后四个服务仍健康，随后 recovery 五阶段成功，复检 `remaining_missing=0`。E13/E14 汇总运行日志扫描 978 个文本文件，0 hits、0 errors。

本报告记录的是成员二实测；E13/E14 的 GitHub CI 还未运行，待提交后再记录 CI 结果。
