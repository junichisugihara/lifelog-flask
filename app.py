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
                "property": "date",
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
            date = props["date"]["date"]["start"] if props.get("date") and props["date"].get("date") else "不明"
            category = props["category"]["select"]["name"] if props.get("category") and props["category"].get("select") else "未分類"
            text = "".join([t["plain_text"] for t in props["text"]["rich_text"]]) if props.get("text") and props["text"].get("rich_text") else ""
            results.append({
                "date": date,
                "category": category,
                "text": text
            })

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
            filter={
                "property": "text",
                "rich_text": {
                    "contains": keyword
                }
            },
            sorts=[
                {"property": "date", "direction": "descending"}
            ]
        )

        results = []
        for page in response["results"]:
            props = page["properties"]
            date = props["date"]["date"]["start"] if props.get("date") and props["date"].get("date") else "不明"
            category = props["category"]["select"]["name"] if props.get("category") and props["category"].get("select") else "未分類"
            text = "".join([t["plain_text"] for t in props["text"]["rich_text"]]) if props.get("text") and props["text"].get("rich_text") else ""
            results.append({
                "date": date,
                "category": category,
                "text": text
            })

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ポート指定（Renderで必須）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
