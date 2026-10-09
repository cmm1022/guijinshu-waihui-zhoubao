# Cursor 定时自动化 · 正式上线

触发：**每周一 9:00（北京时间）**。本地已跑通 `python -m src.run_weekly` 后再在 Cursor 里保存自动化。

## 上线前检查

- [ ] 代码已 push 到 Automation 会拉取的仓库与分支（`.env` 勿提交，仅本地或密钥）
- [ ] 本地 `.env` 与 Automation **密钥**一致（见下表）
- [ ] 周一 9:00 任务日：标题日期为 **上周一～上周五**（脚本按 `RUN_DATE` / 当天自动推算）
- [ ] 贵金属篇：渠道 **同花顺**、简介为「行情回顾」**归纳摘要**（≤60 字）、内容同步三家
- [ ] 外汇篇：内容同步 **交通银行**
- [ ] 失败时 Automation 应 non-zero 退出，便于告警

## Automation 配置

| 项 | 内容 |
|----|------|
| 名称 | 周报邮件抓取并发布 CMS |
| 触发 | Cron：每周一 **9:00 北京时间**（若界面为 UTC：`0 9 * * 1` 等价为 UTC 周一 1:00 ≈ 北京 9:00，**以界面时区说明为准**） |
| 仓库 | 本仓库及默认分支 |
| 模型 | 可运行终端 + 浏览器的 Cloud Agent |

### 密钥（Automation Secrets）

| 变量 | 说明 |
|------|------|
| `EMAIL_USER` | 收信企业邮箱 |
| `EMAIL_PASSWORD` | Foxmail 客户端专用密码 |
| `IMAP_HOST` | 如 `mail.myhexin.com` |
| `IMAP_PORT` | IMAP 一般为 `993` |
| `CMS_EMAIL` / `CMS_PASSWORD` | CMS 密码登录 |
| `CMS_BASE_URL` | 默认 `https://prenewcms.wewecall.com:5443` |

### 建议一并写入的环境变量（非密钥）

| 变量 | 建议值 |
|------|--------|
| `CMS_EDITOR_URL` | `https://prenewcms.wewecall.com:5443/editor/publish-home?pulishType=ARTICLE&back=contentList` |
| `CMS_BROWSER_CHANNEL` | `msedge`（云环境若无 Edge 可改为 `chromium` 并 `playwright install chromium`） |
| `CMS_HEADLESS` | `1`（云端无界面） |

可选：`CMS_DRY_RUN=1` 做首次云端试跑（只打印不发布）。

## Agent 指令（粘贴到自动化说明）

```
在本仓库根目录执行每周周报任务：

1. python -m pip install -r requirements.txt
2. python -m playwright install msedge
   （若 msedge 不可用则 playwright install chromium，并设置 CMS_BROWSER_CHANNEL=chromium）
3. 设置 CMS_HEADLESS=1
4. 运行：python -m src.run_weekly
5. 若任一步失败：输出完整 stderr/stdout，以非零退出码结束，不要静默跳过。

密码与账号仅从 Automation 密钥读取，不要从代码或聊天记录读取。
```

## 本地对照命令

```powershell
cd "D:\cursor项目\贵金属外汇周报"
$env:CMS_HEADLESS='0'
$env:CMS_BROWSER_CHANNEL='msedge'
python -m src.run_weekly
```

试跑单篇：`$env:PUBLISH_ONLY='贵金属'` 或 `'外汇'`。
