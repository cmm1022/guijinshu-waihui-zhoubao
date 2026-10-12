# Automation 用户消息（周报 CMS）

将下面整段粘贴到 Cursor Automation 的用户消息框。仓库、cron、Secrets 见 [docs/cloud-agent-setup.md](../docs/cloud-agent-setup.md)。

---

在本仓库根目录执行每周周报任务：

1. `bash scripts/run_automation_weekly.sh`（推荐；内部使用 `python3`）
2. 或手动：`python3 -m pip install -r requirements.txt` → `python3 -m playwright install` → `CMS_HEADLESS=1 python3 -m src.run_weekly`（勿用 `python -m`，Linux 云镜像默认无 `python` 会 exit 127）
3. `CMS_BROWSER_CHANNEL` 须与 `playwright install` 安装的浏览器一致（见 Secrets）
4. 任一步失败：输出完整 stderr/stdout，以非零退出码结束，不要静默跳过。

账号密码仅从 Automation Secrets 读取，不要从聊天记录读取。
