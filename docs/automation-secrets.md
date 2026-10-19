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

### 收信与 CMS 基础（必填）

| 密钥名 | 说明 |
|--------|------|
| `EMAIL_USER` | 收信企业邮箱 |
| `EMAIL_PASSWORD` | Foxmail 客户端专用密码 |
| `IMAP_HOST` | 如 `mail.myhexin.com` |
| `IMAP_PORT` | `993` |
| `MAIL_SENDER` | `webdetect@myhexin.com`（可选，代码有默认） |
| `CMS_BASE_URL` | `https://prenewcms.wewecall.com:5443` |
| `CMS_EDITOR_URL` | 编辑页 URL（见 `.env.example`） |
| `CMS_BROWSER_CHANNEL` | 云端建议 `chromium` |
| `CMS_HEADLESS` | `1` |
| `REPORT_TZ` | `Asia/Shanghai`（标题「上周一～五」按北京时间；避免 UTC 周一清晨仍算成周日） |

### 分租户发布（当前推荐，`CMS_PUBLISH_MODE=per_tenant`）

| 密钥名 | 说明 |
|--------|------|
| `CMS_PUBLISH_MODE` | `per_tenant` |
| `CMS_TENANT_PUBLISHERS` | 租户 JSON 一行（邮箱 + `password_env`，见 [分租户发布.md](./分租户发布.md)） |
| `CMS_TENANT_ZRCUB_PASSWORD` | 浙江省联社 CMS 密码 |
| `CMS_TENANT_PSBC_PASSWORD` | 邮储银行 CMS 密码 |
| `CMS_TENANT_HZBANK_PASSWORD` | 杭州银行 CMS 密码 |
| `CMS_TENANT_BCM_PASSWORD` | 交通银行 CMS 密码 |

分租户模式下 **`CMS_EMAIL` / `CMS_PASSWORD` 可不配**（各租户用自己账号登录）。

### 运营账号 + 内容同步（旧方式，可选）

| 密钥名 | 说明 |
|--------|------|
| `CMS_EMAIL` | 同花顺运营 CMS 邮箱 |
| `CMS_PASSWORD` | 运营 CMS 密码 |
| `CMS_FORCE_OPERATOR_SYNC` | 设为 `1` 时即使配了租户列表也走运营账号同步 |

### 与定时任务无关（仅本地同步脚本用）

| 密钥名 | 说明 |
|--------|------|
| `CURSOR_API_KEY` | [Settings → API Keys](https://cursor.com/dashboard?tab=settings) 创建；**仅**用于 `sync_cursor_cloud_secrets.py` 把 `.env` 批量写入 Cloud，**不会**被 `run_weekly` 读取。可只在使用脚本时临时设置，不必长期写在 `.env`。 |

## 和 Automation 的关系

1. 在 **Automations** 里编辑「周报邮件抓取并发布 CMS」。  
2. **Environment / Cloud environment**：必须选中 **上面配置了 Secrets 的那个环境**，不要选 “No environment”。  
3. **Repository**：`cmm1022/guijinshu-waihui-zhoubao`，分支 `main`。  
4. 若改环境后仍读不到变量：在该 Automation 里 **重新选一次 Environment 并 Save**（避免旧的 Skip install 导致不注入 Secrets）。

本地对照 `.env` 时，可在终端运行（**不打印密码**，会显示发布模式与租户列表）：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_automation_env.ps1
# 或
python scripts/check_weekly_env.py
```

粘贴值可用：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\copy_secrets_for_automation.ps1
```

（脚本把 `.env` 的值逐条复制到剪贴板，你在 **Cloud Agents → 该环境 → Secrets** 里粘贴即可。）
