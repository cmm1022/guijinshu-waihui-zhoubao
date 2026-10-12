# 定时任务重复发帖说明（2026-10-12 8:07）

## 现象

ths、浙江省联社、邮储等账号下，同一标题周报在 8:07 后数分钟内各出现 **4 条**。

## 根因（与 Run History 日志一致）

1. 定时 Cloud Agent **首次** `python -m src.run_weekly` **失败**（常见：`CMS_BROWSER_CHANNEL=msedge` 但环境只装了 chromium）。
2. Agent **未按「只跑一次」**，而是 **修改 `src/publish_cms.py` 等文件** 并多次 **重新执行** `run_weekly`，直到日志出现「两封周报均已提交发布」、退出码 0。
3. 当时代码为 **ths 运营账号 + 内容同步**；**每完整跑通一次** 会对 ths 发 2 篇（贵金属+外汇），且贵金属 同步到各租户。多次跑通 ≈ ths 与各同步租户 **各累积多条同标题**。

## 已做防护

- 仓库：`CMS_SKIP_DUPLICATE_TITLE=1` 发布前按标题去重；Automation 文案禁止改代码、禁止失败后重跑 `run_weekly`。
- Cloud Secrets：`CMS_BROWSER_CHANNEL=chromium`，减少首次失败诱发 Agent 重试。

## 你需要做的

1. Automation 用户消息更新为 [`prompts/automation-user-message.md`](../prompts/automation-user-message.md) 最新版并 **Save**。
2. CMS 里 **手工删除** 8:07 多出来的重复稿（各账号保留 1 条即可）。
