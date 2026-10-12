# Automation 用户消息（周报 CMS）

将下面整段粘贴到 Cursor Automation 的用户消息框。仓库、cron、Secrets 见 [docs/cloud-agent-setup.md](../docs/cloud-agent-setup.md)。

---

在本仓库根目录执行每周周报任务（**只发布、不修代码**）：

1. `python -m pip install -r requirements.txt`
2. `python -m playwright install chromium`（云端 Secrets 中 `CMS_BROWSER_CHANNEL` 应为 `chromium`，与安装一致）
3. 环境变量 `CMS_HEADLESS=1`
4. **仅运行一次** `python -m src.run_weekly`（不要用浏览器再发 CMS）。
5. 若输出含「发布流程已执行完成」且退出码为 0，**立即结束**。
6. **禁止**为排查失败而修改 `src/`、`scripts/` 等仓库文件；**禁止**在失败后再次运行 `run_weekly`「验证修复」——失败只输出完整 stderr/stdout 并以非零退出码结束，避免重复发帖。
7. 不要使用 Playwright MCP / 浏览器工具手动登录 CMS 发布。

账号密码仅从 Automation Secrets 读取，不要从聊天记录读取。
