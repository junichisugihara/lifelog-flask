from flask import Flask, request, jsonify
from notion_client import Client
import os

app = Flask(__name__)

notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["NOTION_DB_ID"]

@app.route("/searchLifelogByKeyword", methods=["POST"])
def search_lifelog_by_keyword():
    try:
        keyword = request.json.get("keyword")
        if not keyword:
            return jsonify({"error": "Missing keyword"}), 400

        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "property": "text",  # タイトル列
                "title": {
                    "contains": keyword
                }
            },
            sorts=[
                {
                    "property": "DATE",
                    "direction": "descending"
                }
            ]
        )

        results = []
        for page in response["results"]:
            props = page["properties"]

            # DATE
            date = props["DATE"]["date"]["start"] if props.get("DATE") and props["DATE"].get("date") else "不明"

            # カテゴリ
            category = props["カテゴリ"]["select"]["name"] if props.get("カテゴリ") and props["カテゴリ"].get("select") else "未分類"

            # テキスト（タイトル列）
            text = "".join([t["plain_text"] for t in props["text"]["title"]]) if props.get("text") and props["text"].get("title") else ""

            results.append({
                "date": date,
                "category": category,
                "text": text
            })

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
