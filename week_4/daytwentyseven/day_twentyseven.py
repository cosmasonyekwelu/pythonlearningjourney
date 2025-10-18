"""
Day 27 — Frontend Integration & Templates

Focus:
Connecting backend logic with frontend presentation.
Using Jinja2 (Flask) and Django Templates to render dynamic content.
"""

from flask import Flask, render_template, request

app = Flask(__name__)

# Mock data for Trading Dashboard
portfolio_data = {
    "username": "Cosmas",
    "balance": 12000,
    "holdings": [
        {"symbol": "BTC", "amount": 0.3, "value_usd": 9000},
        {"symbol": "ETH", "amount": 1.5, "value_usd": 3000},
    ],
    "recent_trades": [
        {"symbol": "BTC", "action": "BUY", "amount": 0.1, "price": 32000},
        {"symbol": "ETH", "action": "SELL", "amount": 0.5, "price": 2100},
    ],
}


@app.route("/")
def home():
    return render_template("dashboard.html", data=portfolio_data)


@app.route("/trade", methods=["GET", "POST"])
def trade():
    message = ""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        action = request.form.get("action")
        amount = request.form.get("amount")
        price = request.form.get("price")

        # Simple validation
        if not symbol or not amount or not price:
            message = "Please fill out all fields."
        else:
            message = f"Trade recorded: {action} {amount} {symbol} at ${price}"

    return render_template("trade.html", message=message)


if __name__ == "__main__":
    app.run(debug=True)
