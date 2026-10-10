# 把本项目接到 Cursor 在线仓库（Windows）

本机 **Origin CLI 暂不支持原生 Windows**，可用网页创建仓库后关联本地目录。

1. 打开 [cursor.com/codebase](https://cursor.com/codebase) → **New repository**  
   建议名称：`guijinshu-waihui-zhoubao`（或任意未占用名）

本仓库已创建时的远程地址：

`https://origin.cursor.com/guijinshu-waihui-zhoubao/guijinshu-waihui-zhoubao.git`

2. 创建后复制 **HTTPS 克隆地址**（同上格式）
3. **本地已有本项目时不要 `origin repo clone`**（会多出一层目录）。只需 push：

```powershell
cd "D:\cursor项目\贵金属外汇周报"
git remote add origin https://origin.cursor.com/guijinshu-waihui-zhoubao/guijinshu-waihui-zhoubao.git
git push -u origin master
```

（若已添加过 `origin`，改用 `git remote set-url origin <URL>`。）

若提示未登录，在 **弹出的浏览器 / 登录框** 用 Cursor 账号授权后再 push。

**Origin CLI**：安装脚本仅支持 macOS、Linux、**WSL**；原生 Windows 的 Git Bash（MINGW）会报 `unsupported OS`。Windows 上推荐直接用 **Git + HTTPS push**；若要用 `origin auth login` 配置凭据，请在 **WSL Ubuntu** 里安装 CLI。
