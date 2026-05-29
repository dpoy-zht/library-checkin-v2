# 📚 SDUFE 图书馆远程签到系统

> 山东财经大学图书馆签到/暂离/签离的远程解决方案，再见百米冲刺。

---

## 🤔 为什么会有这个项目

校图书馆的规则有一点让人非常头疼：除了中午，临时离开的时间上限仅有 **100 分钟**。

一节课通常是 90 分钟，加上课前课后的路程，100 分钟的往返时间显得格外极限。如果稍有延误导致违约，累计 3 次就要被**禁赛 3 天**。

---

## 🔍 技术分析

在一次签到时，我偶然观察了一下图书馆的签到二维码。解码后发现，它其实就是一段网址加上后缀参数：

```
http://www.skalibrary.net/wx/scancheck?school=sdufe&type=1&t=51526269564
```

参数含义：
- `type=1` → 签到入馆
- `type=2` → 临时离馆
- `type=3` → 签离出馆
- `t=xxx` → 服务器时间戳（非标准 Unix 时间戳）

核心问题：**参数 `t` 是什么？**

从长数字的形式来看像时间戳，但对比几次不同时间生成的二维码后发现并非标准时间戳，而是图书馆服务器内部的时间逻辑。

经过调试，发现图书馆 API：
```
https://libst.sdufe.edu.cn/api.php/v3qrtime
```

返回数据：
```json
{
  "data": 51527920447,
  "msg": "服务器时间",
  "status": 1
}
```

`data` 刚好能和二维码里的 `t` 对应上 ✅

---

## 🏗️ 架构设计

```
用户手机 (SDUFE WiFi)
      │
      │ ① 访问 Flask 页面
      ▼
┌─────────────────────────────┐
│   Flask 后端                 │
│                              │
│  ➤ /api/checkin  生成链接    │──② 代理请求──▶ libst.sdufe.edu.cn
│  ➤ /api/timestamp 获取时间戳  │                 (获取 t 参数)
└─────────────────────────────┘
      │
      │ ③ 返回签到链接
      ▼
用户手动点击 "跳转到图书馆"
      │
      │ ④ 跳转 (保留微信 Cookie)
      ▼
skalibrary.net/wx/scancheck
      │
      │ ⑤ 签到成功 🎉
```

**两个关键设计决策：**

| 问题 | 原因 | 方案 |
|------|------|------|
| `"异常访问"` | 浏览器直连 API 被拒 | 后端代理 + Referer/UA 伪装 |
| `"非法请求"` | JS 自动跳转丢 Cookie | 用户**手动点击链接** |

---

## 🚀 本地运行

```bash
# 1. 安装依赖
pip install flask requests

# 2. 启动
python app.py

# 3. 手机连 SDUFE WiFi，浏览器访问
http://<电脑IP>:5000
```

密码：`zhtzht8888`

---

## 📂 项目结构

```
library-checkin-v2/
├── app.py                # Flask 后端（代理 API + 生成签到链接）
├── templates/
│   └── index.html        # 前端页面（移动端优化）
├── requirements.txt
└── README.md
```

---

## 📡 部署

本地运行即可，如需公网访问可考虑：
- Cloudflare Tunnel
- ngrok / frp 内网穿透
- Heroku / Render / Railway 免费额度

---

*Powered by Flask + ❤️*
