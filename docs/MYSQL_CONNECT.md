# 新机连接 MySQL（泰迪杯工程）

本工程通过 **`.env`** 中的 **`TEDDY_MYSQL_DSN`** 连接数据库，应用使用 **`pymysql`**（见 `finance_agent_rag/core/database/db.py`）。

**DSN 格式**（密码中的特殊字符需做 **URL 编码**，见文末）：

```text
mysql+pymysql://用户名:密码@主机:端口/库名
```

**示例**（本机、默认端口、库名与 `schema.sql` 一致）：

```text
TEDDY_MYSQL_DSN=mysql+pymysql://root:你的密码@127.0.0.1:3306/teddy_b
```

---

## 场景 A：MySQL 装在新机本机（推荐先这样跑通）

### A1. 安装 MySQL

- Windows：从 [MySQL 官方](https://dev.mysql.com/downloads/mysql/) 或「MySQL Installer」安装 **MySQL Server**，记住 **root 密码**与 **端口**（默认 **3306**）。  
- 或安装 **XAMPP / WSL 里的 MySQL** 等，只要你能用客户端连上即可。

### A2. 建库、建表

1. 用 **MySQL Workbench**、**命令行 `mysql`** 或 **HeidiSQL** 等登录（`127.0.0.1:3306`，用户/密码为安装时设置）。  
2. 在仓库中打开 **`finance_agent_rag/core/database/schema.sql`**，**整文件执行**（会 `CREATE DATABASE teddy_b` 并建四张表）。  
3. 在左侧或 `SHOW DATABASES;` 中确认存在 **`teddy_b`**。

### A3. 项目里写 `.env`

在**仓库根目录**（与 `main.py` 同级）创建 **`.env`**（可从 **`.env.example`** 复制）：

```env
TEDDY_MYSQL_DSN=mysql+pymysql://root:你的实际密码@127.0.0.1:3306/teddy_b
```

保存后，在仓库根执行（验证 Python 能连上）：

```bash
python -c "from finance_agent_rag.core.database.db import get_connection; c=get_connection(); c.close(); print('MySQL OK')"
```

若报错，对照「第五节 常见问题」。

---

## 场景 B：MySQL 在「另一台电脑 / 老机器」上，新机要连过去

目标：SQL 在 **A 电脑**，**B 电脑** 只跑本工程，通过**局域网 IP** 连 A 的 3306。

### B1. 在 A 电脑（装 MySQL 的那台）上

1. **建库、建表**（同场景 A2），确保 **`teddy_b`** 可登录。  
2. **为远程连接建账号**（二选一；**不要用弱密码**）  
   - 若继续用 `root` 远程：很多默认只允许 `localhost`，需单独授权。  
   - 推荐**单独用户**（示例）：

   ```sql
   CREATE USER 'teddy'@'%' IDENTIFIED BY '强密码';
   GRANT ALL PRIVILEGES ON teddy_b.* TO 'teddy'@'%';
   FLUSH PRIVILEGES;
   ```

   若只允许你办公室网段，可把 `'%'` 改成 `192.168.1.%` 等（按你网段改）。

3. **让 MySQL 监听外网/局域网**  
   编辑 MySQL 配置 **`my.ini`**（Windows 通常在安装目录下）中 **`[mysqld]`**：

   ```ini
   bind-address = 0.0.0.0
   ```

   改完后**重启** MySQL 服务（「服务」里找 MySQL 或安装器里 Restart）。

4. **Windows 防火墙** 放行 **入站** TCP **3306**（或你实际端口）：  
   「高级安全 Windows Defender 防火墙」→ 入站规则 → 新建规则 → 端口 → TCP 3306 → 允许。

5. 查 A 电脑 **局域网 IP**：在 A 上 `cmd` 执行 `ipconfig`，看 **IPv4**（如 `192.168.1.100`）。  
6. 在 **A 本机**先测试：`mysql -h 127.0.0.1 -P 3306 -u teddy -p` 能进 `teddy_b`；再在**同一网段另一台设备**上（若有 `mysql` 客户端）试：`mysql -h 192.168.1.100 -P 3306 -u teddy -p`。

### B2. 在 B 电脑（新机、跑本仓库）

在仓库根 **`.env`** 里把**主机**写成 A 的 IP，用户用上面建好的账号：

```env
TEDDY_MYSQL_DSN=mysql+pymysql://teddy:强密码@192.168.1.100:3306/teddy_b
```

再执行 A3 的 `python -c` 测连接。

> **公网/云服务器**：把 `bind-address`、防火墙、安全组**一起**放行 3306，并**强密码** + 尽量**禁止 root 远程**；生产环境建议 **VPN/SSH 隧道** 或云厂商托管 MySQL，不裸漏 3306 到公网。

---

## 场景 C：云数据库 / 内网隧道

- **云 RDS**（阿里云、腾讯云等）：控制台给出**外网/内网地址、端口、账号、库名**，把 `host:port` 和账号密码填进 **DSN** 即可；若需 SSL，需后续在代码里扩展 `pymysql` 的 `ssl` 参数（当前 `db.py` 未加 SSL 字段）。  
- **只开 SSH 隧道**（不开放 3306 到公网）：在 B 上 `ssh -L 3307:127.0.0.1:3306 user@A`，则 B 上 DSN 可写 `127.0.0.1:3307` 指向本机转发的隧道。

---

## 密码与特殊字符（URL 编码）

DSN 在 URL 里，若密码含 `@ : / #` 等，需 **URL 编码**后再写入 `.env`：

| 字符 | 编码  |
|------|-------|
| `@`  | `%40` |
| `:`  | `%3A` |
| `/`  | `%2F` |
| `#`  | `%23` |
| 空格 | `%20` |

或在 MySQL 里给该账号**换不含特殊字符的密码**，避免 URL 问题。

---

## 常见问题

| 现象 | 处理 |
|------|------|
| `未配置 MySQL` / DSN 为空 | 根目录要有 `.env` 且含 `TEDDY_MYSQL_DSN=...`；或设置**系统环境变量**同名。 |
| `Can't connect to MySQL server` | 查 IP/端口、MySQL 是否启动、A 的防火墙、**bind-address**、是否同一局域网。 |
| `Access denied` | 用户/密码错；或该用户**不允许从你这台机器的 Host 登录**（改 `GRANT ...@'%'` 或具体 IP）。 |
| `Unknown database 'teddy_b'` | 在服务器上执行 `schema.sql` 建库。 |

---

## 与 `PROJECT_HANDOFF.md` 的关系

建库、跑任务一全链路前，**先完成本页连接测试**，再大文件跑 `task1_pipeline`（会 UPSERT 写入 `teddy_b`）。
