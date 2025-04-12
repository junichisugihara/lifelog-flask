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

        # 形式統一（例: 4/12 → 04-12）
        mmdd_formatted = mmdd.replace("/", "-").zfill(5)
        if len(mmdd_formatted) == 4:
            mmdd_formatted = "0" + mmdd_formatted  # 4-5 → 04-05

        results = []
        start_cursor = None

        while True:
            response = notion.databases.query(
                database_id=DATABASE_ID,
                start_cursor=start_cursor,
                page_size=100,
                filter={
                    "property": "DATE",
                    "date": {
                        "contains": mmdd_formatted
                    }
                },
                sorts=[
                    {
                        "property": "DATE",
                        "direction": "descending"
                    }
                ]
            )

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

            if not response.get("has_more"):
                break
            start_cursor = response["next_cursor"]

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
