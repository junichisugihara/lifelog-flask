from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "Lifelog API is running!"

@app.route("/search", methods=["GET"])
def test_dummy():
    mmdd = request.args.get("mmdd", "未指定")
    return jsonify({
        "results": [
            {
                "date": f"2025-{mmdd}",
                "category": "テスト",
                "text": f"これは {mmdd} のテストデータです"
            }
        ]
    })

# Render用ポート指定
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
