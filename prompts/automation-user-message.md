# Automation 用户消息（周报 CMS）

将下面整段粘贴到 Cursor Automation 的用户消息框。仓库、cron、Secrets 见 [docs/cloud-agent-setup.md](../docs/cloud-agent-setup.md)。

---

在本仓库根目录执行每周周报任务（**推荐一条命令**）：

```bash
bash scripts/run_automation_weekly.sh
```

或手动逐步执行（Linux Cloud 仅有 `python3` 时，请用 `python3` 代替 `python`，并保证 `PATH` 含 `$HOME/.local/bin`）：

1. `python3 -m pip install -r requirements.txt`
2. `python3 -m playwright install "$CMS_BROWSER_CHANNEL"`（通道与 Secrets 中 `CMS_BROWSER_CHANNEL` 一致；失败时可换 `msedge` 并重试）
3. 环境变量 `CMS_HEADLESS=1`
4. 运行 `python3 -m src.run_weekly`
5. 任一步失败：输出完整 stderr/stdout，以非零退出码结束，不要静默跳过。

账号密码仅从 Automation Secrets 读取，不要从聊天记录读取。
