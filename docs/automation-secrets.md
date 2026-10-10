# 密钥（Secrets）填在哪里？

**不在** Automations 新建/编辑页里。和热点板块一样，要在 **Cloud Agents 的环境** 里配置，定时任务运行时才会注入成环境变量。

## 操作路径（推荐）

1. 浏览器打开 **Cursor 控制台** → **Cloud Agents**（或 Cloud）：  
   https://cursor.com/dashboard?tab=cloud-agents  
2. 找到/创建与 **GitHub `cmm1022/guijinshu-waihui-zhoubao`** 关联的 **Environment**（环境）。  
   - 若已有该仓库的环境，点进去。  
   - 若没有：在环境里 **添加仓库** `cmm1022/guijinshu-waihui-zhoubao`，或从仓库页「Start setup agent」走一遍引导。  
3. 进入该环境详情页后，在 **右侧边栏** 或 **Secrets** 标签页 → **Add secret** / **Add variable**。  
4. **Name** 填下表变量名，**Value** 填与本地 `.env` 相同的值（勿提交 Git）。

也可尝试直达（需已登录 Cursor，且环境已创建）：

`https://cursor.com/dashboard/cloud-agents/environments/r/github.com/cmm1022/guijinshu-waihui-zhoubao`

## 变量清单

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
| `CMS_BROWSER_CHANNEL` | 云端建议 `chromium` |
| `CMS_HEADLESS` | `1` |

## 和 Automation 的关系

1. 在 **Automations** 里编辑「周报邮件抓取并发布 CMS」。  
2. **Environment / Cloud environment**：必须选中 **上面配置了 Secrets 的那个环境**，不要选 “No environment”。  
3. **Repository**：`cmm1022/guijinshu-waihui-zhoubao`，分支 `main`。  
4. 若改环境后仍读不到变量：在该 Automation 里 **重新选一次 Environment 并 Save**（避免旧的 Skip install 导致不注入 Secrets）。

本地对照 `.env` 时，可在终端运行（只检查变量名是否齐全，不打印密码）：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_automation_env.ps1
```

粘贴值可用：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\copy_secrets_for_automation.ps1
```

（脚本把 `.env` 的值逐条复制到剪贴板，你在 **Cloud Agents → 该环境 → Secrets** 里粘贴即可。）
