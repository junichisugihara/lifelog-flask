@app.route("/getLifelogByDate", methods=["POST"])
def get_lifelog_by_date():
    try:
        mmdd = request.json.get("mmdd")
        if not mmdd:
            return jsonify({"error": "Missing mmdd"}), 400

        # 形式を統一（例: 4/5 → 04-05）
        mmdd = mmdd.replace("/", "-").zfill(5)
        if len(mmdd) == 4:
            mmdd = "0" + mmdd  # 例: 4-5 → 04-05

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

                # MM-DD 抽出
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
