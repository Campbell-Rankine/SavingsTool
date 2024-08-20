from flask import Flask, render_template, request, redirect, url_for
from tinydb import TinyDB, Query
import random

from main import run_calc

app = Flask(__name__)
# createing typedb
db = TinyDB("data.json")


@app.route("/")
def root():
    todo_list = db.all()
    return render_template("index.html", todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    # add new item
    name = str(request.form.get("firstName"))
    days = int(request.form.get("numDays"))
    value = run_calc(name, days)
    print(name, days, value)
    db.insert(
        {
            "id": random.randint(0, 1000),
            "firstName": name,
            "daysSearched": days,
            "value": value,
        }
    )
    return redirect(url_for("root"))


@app.route("/update", methods=["POST"])
def update():
    # update the todo titel
    todo_db = Query()
    newTest = request.form.get("inputField")
    todo_id = request.form.get("hiddenField")
    db.update({"firstName": newTest}, todo_db.id == int(todo_id))
    return redirect(url_for("root"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    # delete the todo
    todo_db = Query()
    db.remove(todo_db.id == todo_id)
    return redirect(url_for("root"))


@app.route("/complete/<int:todo_id>")
def complete(todo_id):
    # mark complete
    todo_db = Query()
    db.update({"complete": True}, todo_db.id == todo_id)
    return redirect(url_for("root"))


if __name__ == "__main__":
    app.run(debug=True)
