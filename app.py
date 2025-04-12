from flask import Flask, request, jsonify
from notion_client import Client
import os

app = Flask(__name__)

notion = Client(auth=os.environ["NOTION_TOKEN"])
DATABASE_ID = os.environ["NOTION_DB_ID"]

@app.route("/")
def index():
    return "Lifelog API is running!"

@app.route("/search", methods=["GET"])
def search_lifelog_by_mmdd():
    try:
        mmdd = request.args.get("mmdd")
        if not mmdd:
            return jsonify({"error": "Missing mmdd"}), 400

        # MM-DD形式に確実に変換（例: 4/12 → 04-12）
        parts = mmdd.replace("/", "-").split("-")
        if len(parts) == 2:
            month = parts[0].zfill(2)
            day = parts[1].zfill(2)
            mmdd = f"{month}-{day}"
        else:
            return jsonify({"error": "Invalid mmdd format"}), 400

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
                sorts=[{"property": "DATE", "direction": "descending"}]
            )

            for page in response["results"]:
                props = page["properties"]
                date_str = props["DATE"]["date"]["start"] if props.get("DATE") and props["DATE"].get("date") else None
                if not date_str:
                    continue

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

# Render用ポート指定
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
