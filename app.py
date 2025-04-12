from flask import Flask, request, jsonify
from notion_client import Client
import os

app = Flask(__name__)

notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["NOTION_DB_ID"]

@app.route("/")
def index():
    return "Lifelog API is running!"

@app.route("/getLifelogByDate", methods=["POST"])
def get_lifelog_by_date():
    try:
        mmdd = request.json.get("mmdd")
        if not mmdd:
            return jsonify({"error": "Missing mmdd"}), 400

        # 日付表記を Notion に合わせて統一（例: 4/5 → 04-05）
        mmdd_formatted = mmdd.replace("/", "-").zfill(5)
        if len(mmdd_formatted) == 4:
            mmdd_formatted = "0" + mmdd_formatted  # 4-5 → 04-05

        response = notion.databases.query(
            database_id=DATABASE_ID,
            page_size=100,
            filter={
                "property": "DATE",
                "date": {
                    "contains": mmdd_formatted
                }
            },
            sorts=[
                {"property": "DATE", "direction": "descending"}
            ]
        )

        results = []
        for page in response["results"]:
            props = page["properties"]
            date = props["DATE"]["date"]["start"] if props.get("DATE") and props["DATE"].get("date") else "不明"
            category = props["カテゴリ"]["select"]["name"] if props.get("カテゴリ") and props["カテゴリ"].get("select") else "未分類"
            text = "".join([t["plain_text"] for t in props["text"]["title"]]) if props.get("text") and props["text"].get("title") else ""
            results.append({
                "date": date,
                "category": category,
                "text": text
            })

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Renderでポート公開が必要
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
