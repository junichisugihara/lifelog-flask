from flask import Flask, request, jsonify
from notion_client import Client
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# NotionのAPIトークンとデータベースID
notion = Client(auth="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")
database_id = "1cc4b27b686481c8aac2dfbf70a786a1"

@app.route("/search", methods=["GET"])
def search_by_mmdd():
    mmdd = request.args.get("mmdd")  # 例: 07-09
    if not mmdd:
        return jsonify({"error": "mmdd parameter required"}), 400

    years = range(2012, 2026)
    results = []

    for year in years:
        full_date = f"{year}-{mmdd}"
        try:
            response = notion.databases.query(
                database_id=database_id,
                filter={
                    "property": "DATE",
                    "date": {
                        "equals": full_date
                    }
                }
            )

            for row in response["results"]:
                props = row["properties"]
                date = props["DATE"]["date"]["start"]
                category = props["カテゴリ"]["select"]["name"] if props["カテゴリ"]["select"] else None
                text = props["text"]["title"][0]["plain_text"] if props["text"]["title"] else None

                results.append({
                    "date": date,
                    "year": year,
                    "category": category,
                    "text": text
                })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify(results)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
