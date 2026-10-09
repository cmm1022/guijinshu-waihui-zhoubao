# 把本项目接到 Cursor 在线仓库（Windows）

本机 **Origin CLI 暂不支持原生 Windows**，可用网页创建仓库后关联本地目录。

1. 打开 [cursor.com/codebase](https://cursor.com/codebase) → **New repository**  
   建议名称：`guijinshu-waihui-zhoubao`（或任意未占用名）
2. 创建后复制 **HTTPS 克隆地址**（`https://origin.cursor.com/...`）
3. 在本项目目录执行（PowerShell）：

```powershell
cd "D:\cursor项目\贵金属外汇周报"
git remote add origin <上一步复制的 URL>
git push -u origin master
```

若提示未登录，在浏览器完成 Cursor 账号授权后再 push。

Mac/Linux 或 WSL 也可安装 Origin CLI：`curl -fsSL https://downloads.cursor.com/origin/install.sh | sh`，然后 `origin auth login` 与 `origin repo create <name>`。
