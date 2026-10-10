# Automation 密钥清单

在 Cursor **Automations → Secrets** 中新增下列项（值与本地 `.env` 一致，勿提交 `.env`）。

| 密钥名 | 说明 |
|--------|------|
| `EMAIL_USER` | 收信企业邮箱 |
| `EMAIL_PASSWORD` | Foxmail 客户端专用密码 |
| `IMAP_HOST` | 如 `mail.myhexin.com` |
| `IMAP_PORT` | `993` |
| `MAIL_SENDER` | `webdetect@myhexin.com`（可选，代码有默认） |
| `CMS_BASE_URL` | `https://prenewcms.wewecall.com:5443` |
| `CMS_EMAIL` | CMS 登录邮箱 |
| `CMS_PASSWORD` | CMS 登录密码 |
| `CMS_EDITOR_URL` | 编辑页 URL（见 `.env.example`） |
| `CMS_BROWSER_CHANNEL` | `msedge` 或云端 `chromium` |
| `CMS_HEADLESS` | `1` |

保存 Automation 前：仓库选 **GitHub `cmm1022/guijinshu-waihui-zhoubao` / 分支 `main`**，cron **每周一 9:00（北京时间）**，用户消息见 `prompts/automation-user-message.md`。
