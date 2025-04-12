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

        # 形式統一（例: 4/5 → 04-05）
        mmdd = mmdd.replace("/", "-").zfill(5)
        if len(mmdd) == 4:
            mmdd = "0" + mmdd

        results = []
        start_cursor = None

        while True:
            response = notion.databases.query(
                database_id=DATABASE_ID,
                page_size=100,
                start_cursor=start_cursor,
                filter={
                    "property": "DATE",
                    "date": {
                        "is_not_empty": True
                    }
                },
                sorts=[
                    {"property": "DATE", "direction": "descending"}
                ]
            )

            for page in response["results"]:
                props = page["properties"]
                date_str = props["DATE"]["date"]["start"] if props.get("DATE") and props["DATE"].get("date") else None
                if not date_str:
                    continue

                # MM-DD 抽出して比較
                if date_str[5:10] == mmdd:
                    category = props["カテゴリ"]["select"]["name"] if props.get("カテゴリ") and props["カテゴリ"].get("select") else "未分類"
                    text = "".join([t["plain_text"] for t in props["text"]["title"]]) if props.get("text") and props["text"].get("title") else ""
                    results.append({
                        "date": date_str,
                        "category": category,
                        "text": text
                    })

            if not response.get("has_more"):
                break
            start_cursor = response["next_cursor"]

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/searchLifelogByKeyword", methods=["POST"])
def search_lifelog_by_keyword():
    try:
        keyword = request.json.get("keyword")
        if not keyword:
            return jsonify({"error": "Missing keyword"}), 400

        response = notion.databases.query(
            database_id=DATABASE_ID,
            page_size=100,
            filter={
                "property": "text",
                "title": {
                    "contains": keyword
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

# Renderで動作するようポートを指定
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
