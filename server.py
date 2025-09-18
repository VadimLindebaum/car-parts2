"""
Spare-parts API (Python + Flask)
Reads LE.txt once into memory with pandas.
Provides filtering, pagination, sorting.
"""

from flask import Flask, request, jsonify
import pandas as pd

CSV_FILE = "LE.txt"
DEFAULT_PAGE_SIZE = 30

# Load CSV into memory
def load_csv():
    # kohanda separatorit vastavalt (nt ";" kui vaja)
    df = pd.read_csv(CSV_FILE, sep=",", dtype=str)
    # clean
    df = df.fillna("")
    # hinnakolumn numbriks (kui olemas)
    if "price" in df.columns:
        df["_price"] = (
            df["price"].astype(str)
            .str.replace(r"[^\d.\-]", "", regex=True)
            .astype(float, errors="ignore")
        )
    else:
        df["_price"] = None
    # lowercase nimi
    if "name" in df.columns:
        df["_name"] = df["name"].str.lower()
    else:
        df["_name"] = ""
    # SN normaliseerimine (otsib tavalisi nimesid)
    sn_candidates = ["serial_number", "sn", "serial", "part_number", "partno"]
    sn_col = None
    for c in sn_candidates:
        if c in df.columns:
            sn_col = c
            break
    if sn_col is None:
        sn_col = df.columns[0]  # fallback
    df["_sn"] = df[sn_col].astype(str)
    return df

df = load_csv()

app = Flask(__name__)

@app.route("/")
def health():
    return jsonify({"status": "ok", "rows_loaded": len(df)})

@app.route("/spare-parts")
def spare_parts():
    global df
    filtered = df

    # query params
    name = request.args.get("name")
    sn = request.args.get("sn")
    search = request.args.get("search")
    sort = request.args.get("sort")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", DEFAULT_PAGE_SIZE))

    # filtering
    if name:
        filtered = filtered[filtered["_name"].str.contains(name.lower(), na=False)]
    if sn:
        filtered = filtered[filtered["_sn"].str.contains(sn, na=False)]
    if search:
        mask = filtered["_name"].str.contains(search.lower(), na=False) | filtered["_sn"].str.contains(search, na=False)
        filtered = filtered[mask]

    # sorting
    if sort:
        desc = False
        key = sort
        if sort.startswith("-"):
            desc = True
            key = sort[1:]
        if key == "price":
            key = "_price"
        elif key == "sn":
            key = "_sn"
        elif key == "name":
            key = "_name"
        if key in filtered.columns:
            filtered = filtered.sort_values(by=key, ascending=not desc)

    # pagination
    total = len(filtered)
    total_pages = max(1, -(-total // page_size))  # ceiling division
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    data = filtered.iloc[start:end].to_dict(orient="records")

    return jsonify({
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "data": data
    })

@app.route("/spare-parts/<sn>")
def get_by_sn(sn):
    global df
    result = df[df["_sn"].str.contains(sn, na=False)]
    return jsonify({"total": len(result), "data": result.to_dict(orient="records")})

@app.route("/reload", methods=["POST"])
def reload():
    global df
    df = load_csv()
    return jsonify({"status": "reloaded", "rows": len(df)})

if __name__ == "__main__":
    app.run(port=3300, debug=True)
