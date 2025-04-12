from flask import Flask, request, jsonify
from notion_client import Client
import os

app = Flask(__name__)

notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["NOTION_DB_ID"]

@app.route("/getLifelogByDate", methods=["POST"])
def get_lifelog_by_date():
    try:
        mmdd = request.json.get("mmdd")
        if not mmdd:
            return jsonify({"error": "Missing mmdd"}), 400

        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "property": "DATE",
                "date": {
                    "contains": mmdd
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
        return jsonify({"error": str(e)}), 200  # <= ここを 500 から 200 にして、NotFoundも正常応答扱いに
@app.route("/")
def index():
    return "Lifelog API is running!"
