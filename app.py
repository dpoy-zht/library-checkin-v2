"""
SDUFE 图书馆远程签到系统 - Flask 后端
核心思路：后端代理 API 请求获取时间戳，前端展示手动点击链接（保留微信登录态）
"""
from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# 图书馆 API
LIBRARY_TIMESTAMP_API = "https://libst.sdufe.edu.cn/api.php/v3qrtime"
LIBRARY_CHECKIN_URL   = "http://www.skalibrary.net/wx/scancheck"
SCHOOL_CODE           = "sdufe"

# 模拟微信内置浏览器请求头，绕过 API 来源检查
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.48",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://libst.sdufe.edu.cn/",
    "Origin": "https://libst.sdufe.edu.cn",
    "X-Requested-With": "XMLHttpRequest",
}

TYPE_NAMES = {"1": "签到入馆", "2": "临时离馆", "3": "签离出馆"}


def fetch_timestamp():
    """从图书馆 API 获取服务器时间戳，返回 (success: bool, data: str|int)"""
    resp = requests.get(LIBRARY_TIMESTAMP_API, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") == 1 and data.get("data"):
        return True, data["data"]
    return False, data.get("msg", "时间戳获取失败")


# ===================== 页面路由 =====================

@app.route("/")
def index():
    return render_template("index.html")


# ===================== API 路由 =====================

@app.route("/api/timestamp")
def api_timestamp():
    """代理获取时间戳（供前端轮询/验证用）"""
    try:
        ok, result = fetch_timestamp()
        if ok:
            return jsonify({"success": True, "timestamp": result})
        return jsonify({"success": False, "msg": result}), 400
    except Exception as e:
        return jsonify({"success": False, "msg": f"服务器错误: {str(e)}"}), 500


@app.route("/api/checkin", methods=["POST"])
def api_checkin():
    """生成签到链接（后端代理获取时间戳 + 拼接 URL）"""
    try:
        data = request.get_json(silent=True) or {}
        action_type = str(data.get("type", "1"))

        if action_type not in ("1", "2", "3"):
            return jsonify({"success": False, "msg": "无效的操作类型，请选择 1/2/3"}), 400

        ok, result = fetch_timestamp()
        if not ok:
            return jsonify({"success": False, "msg": result}), 400

        timestamp = result
        url = f"{LIBRARY_CHECKIN_URL}?school={SCHOOL_CODE}&type={action_type}&t={timestamp}"

        return jsonify({
            "success": True,
            "url": url,
            "type": action_type,
            "name": TYPE_NAMES[action_type],
            "timestamp": timestamp,
        })
    except Exception as e:
        return jsonify({"success": False, "msg": f"服务器错误: {str(e)}"}), 500


# ===================== 启动 =====================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
