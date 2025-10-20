# app.py

from flask import Flask, render_template, request, redirect
import sqlite3
import pandas as pd
from datetime import date
import os
from utils import init_db

app = Flask(__name__)
DATA_PATH = "data/data.db"

# ✅ Initialize DB
init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        date_entry = request.form["date"]
        worker_name = request.form["worker_name"]
        cotton_kg = float(request.form["cotton_kg"])
        rate_per_kg = float(request.form["rate_per_kg"])
        sale_rate_quintal = float(request.form["sale_rate_quintal"])

        conn = sqlite3.connect(DATA_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO records (date, worker_name, cotton_kg, rate_per_kg, sale_rate_quintal)
            VALUES (?, ?, ?, ?, ?)
        """, (date_entry, worker_name, cotton_kg, rate_per_kg, sale_rate_quintal))
        conn.commit()
        conn.close()
        return redirect("/dashboard")

    today = date.today().isoformat()
    return render_template("index.html", today=today)

@app.route("/dashboard", methods=["GET"])
def dashboard():
    conn = sqlite3.connect(DATA_PATH)

    # Read full table into DataFrame
    df = pd.read_sql_query("SELECT * FROM records", conn)

    # ✅ Fetch distinct worker names for dropdown
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT worker_name FROM records")
    worker_names = [row[0] for row in cursor.fetchall()]

    conn.close()

    # Handle filters
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    search_name = request.args.get("worker_name")

    if start_date and end_date:
        df = df[df['date'].between(start_date, end_date)]

    if search_name:
        df = df[df['worker_name'] == search_name]

    # Calculations
    total_cotton = df['cotton_kg'].sum()
    total_payment = (df['cotton_kg'] * df['rate_per_kg']).sum()
    revenue = (df['cotton_kg'] * df['sale_rate_quintal'] / 100).sum()
    profit = revenue - total_payment

    # Chart data
    chart_labels = df['date'].tolist()
    chart_cotton = df['cotton_kg'].tolist()
    chart_profit = ((df['cotton_kg'] * df['sale_rate_quintal'] / 100) - (df['cotton_kg'] * df['rate_per_kg'])).tolist()

    return render_template("dashboard.html",
                           tables=df.to_dict(orient="records"),
                           total_cotton=total_cotton,
                           total_payment=total_payment,
                           revenue=revenue,
                           profit=profit,
                           labels=chart_labels,
                           cotton=chart_cotton,
                           profit_data=chart_profit,
                           start_date=start_date,
                           end_date=end_date,
                           search_name=search_name,
                           worker_names=worker_names)

@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_entry(record_id):
    conn = sqlite3.connect(DATA_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")




if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

