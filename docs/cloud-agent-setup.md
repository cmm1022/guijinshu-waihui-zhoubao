# Cloud Agent 部署说明（GitHub）

与 [热点板块定时任务](https://github.com/cmm1022/hot-sector-analysis) 相同：**Automation 绑定 GitHub 仓库**，Secrets 在 Cursor Cloud 配置，代码 push 到 GitHub。

**状态（2026-10-10）**：本地试跑通过；Cloud 环境 `guijinshu-waihui-zhoubao` 已同步 Secrets。保存 Automation 后 **每周一 9:00（北京时间）** 正式执行。

## 1. 仓库

| 项 | 值 |
|----|-----|
| GitHub | `https://github.com/cmm1022/guijinshu-waihui-zhoubao` |
| 默认分支 | `main` |
| 入口 | `python -m src.run_weekly` |

首次在 GitHub 新建 **私有** 仓库 `guijinshu-waihui-zhoubao`（空仓库即可，不要勾选 README），再在本机 push：

```powershell
cd "D:\cursor项目\贵金属外汇周报"
git remote set-url origin https://github.com/cmm1022/guijinshu-waihui-zhoubao.git
git branch -M main
git push -u origin main
```

## 2. Automation Secrets

变量清单见 [automation-secrets.md](automation-secrets.md)。本地辅助：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\copy_secrets_for_automation.ps1
```

## 3. Automations 配置

| 项 | 值 |
|----|-----|
| 名称 | 周报邮件抓取并发布 CMS |
| 仓库 | `cmm1022/guijinshu-waihui-zhoubao`，分支 `main` |
| Cron | 每周一 **9:00 北京时间**（UTC 常为 `0 1 * * 1`，以界面为准） |
| 用户消息 | [prompts/automation-user-message.md](../prompts/automation-user-message.md) |

云端建议环境变量：`CMS_HEADLESS=1`，`CMS_BROWSER_CHANNEL=chromium`（云环境优先 chromium）。

**内容同步**：贵金属 = 邮储银行、浙江省联社、杭州银行各 1 项；外汇 = 下拉中 **两个「交通银行」均勾选**（脚本会跳过已选、逐一点未选同名项，并在发布前校验数量）。

## 4. 本地试跑

```powershell
$env:CMS_HEADLESS='0'
$env:CMS_BROWSER_CHANNEL='msedge'
python -m src.run_weekly
```
