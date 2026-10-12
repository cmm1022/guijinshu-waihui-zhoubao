# Automation 用户消息（周报 CMS）

将下面整段粘贴到 Cursor Automation 的用户消息框。仓库、cron、Secrets 见 [docs/cloud-agent-setup.md](../docs/cloud-agent-setup.md)。

---

在本仓库根目录执行每周周报任务：

1. `python -m pip install -r requirements.txt`
2. `python -m playwright install chromium`（若失败再试 `msedge`；Secrets 中 `CMS_BROWSER_CHANNEL` 与安装一致）
3. 环境变量 `CMS_HEADLESS=1`
4. **仅运行一次** `python -m src.run_weekly`（不要重复执行、不要用浏览器再发一遍 CMS）。
5. 若输出含「发布流程已执行完成」且退出码为 0，**立即结束**，不要因「确认是否成功」而再次运行第 4 步。
6. 任一步失败：输出完整 stderr/stdout，以非零退出码结束，不要静默跳过。

账号密码仅从 Automation Secrets 读取，不要从聊天记录读取。
