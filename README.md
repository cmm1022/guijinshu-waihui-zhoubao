# 贵金属 / 外汇周报 · 邮件抓取与 CMS 发布

每周从企业邮箱读取 `webdetect@myhexin.com` 发来的「贵金属周报」「外汇周报」（各取最新一封），保留邮件 HTML 排版发布到 [内容管理平台](https://prenewcms.wewecall.com:5443/login)。贵金属简介为「行情回顾」归纳摘要（≤60 字）。

## 1. 企业邮箱协议怎么查（Foxmail）

Foxmail 本身不单独发明一种「Foxmail 协议」，它只是客户端；你在 Foxmail 里配的是什么收信服务器，脚本就用什么——几乎都是 **IMAP**（推荐）或 POP3。周报脚本使用 **IMAP**。

**在 Foxmail 里查看（约 1 分钟）：**

1. 打开 Foxmail → 右上角 **设置**（或菜单 **工具 → 账号管理**）  
2. **账号** 列表里选中你用来收周报的企业邮箱（@myhexin.com）  
3. 打开 **服务器**（或 **高级**）  
4. 看 **收件服务器** 类型是否为 **IMAP**，记下 **服务器地址** 和 **端口**（SSL 常见 **993**）

把地址、端口填进 `.env` 的 `IMAP_HOST`、`IMAP_PORT`。同花顺企邮常见为 `mail.myhexin.com` + `993`；**若 Foxmail 里显示不同，以 Foxmail 为准**。

Foxmail 能正常收信 + 你已开通 **客户端专用密码** → 脚本里 `EMAIL_PASSWORD` 填该专用密码即可（不是 CMS 密码）。

登录密码使用你已开通的 **客户端专用密码**（填 `EMAIL_PASSWORD`）。  
`EMAIL_USER` 填 **你自己收信的邮箱全称**（不是发件人 `webdetect@myhexin.com`）。

## 2. 本地配置

```powershell
cd "D:\cursor项目\贵金属外汇周报"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install msedge
copy .env.example .env
# 编辑 .env 填入 EMAIL_*、CMS_*
```

仅测收信（不发布）：配置 `EMAIL_*` 与 `IMAP_*` 后执行 `python -m src.test_imap`。完整流程还需 CMS 账号。

CMS 发布默认 `CMS_OPEN_EDITOR=direct`（登录后直接打开编辑页 URL，与「发布→文章」新开标签相同）。若坚持用列表点「发布」，设 `CMS_OPEN_EDITOR=ui` 且 `$env:CMS_HEADLESS='0'` 最大化 Edge。

探测 CMS 登录后菜单（需填 CMS 账号，会弹出浏览器）：

```powershell
python -m src.probe_cms
```

若自动找不到「新建文章」，把浏览器里新建页的 path 配到 `CMS_NEW_ARTICLE_PATH`。

## 3. 手动跑一次

```powershell
python -m src.run_weekly
```

## 4. Cursor 定时自动化（每周一 9:00 北京时间）

与热点板块相同，绑定 **GitHub** 仓库。见 **[docs/cloud-agent-setup.md](docs/cloud-agent-setup.md)**、**[docs/三步完成上线.md](docs/三步完成上线.md)**。

要点：push 到 `cmm1022/guijinshu-waihui-zhoubao`；Secrets 配齐 `EMAIL_*`、`IMAP_*`、`CMS_*`；云端 `CMS_HEADLESS=1` 后执行 `python -m src.run_weekly`。

## 5. 说明

- CMS 无开放 API，发布依赖 Playwright；后台 UI 变更时需更新 `publish_cms.py` 或 `CMS_NEW_ARTICLE_PATH`。
- 登录页默认是「验证码登录」，脚本会自动切到 **密码登录**（邮箱 + 密码）。
