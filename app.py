from flask import Flask, render_template, request, redirect, flash
import boto3
import os
from dotenv import load_dotenv

# Завантаження змінних середовища з .env
load_dotenv()

# Ініціалізація Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

s3 = boto3.client("s3")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        folder_name = request.form.get("folder_name", "").strip()
        if folder_name:
            if not folder_name.endswith("/"):
                folder_name += "/"
            try:
                s3.put_object(Bucket="student-website-vbohuslavskyi-2025", Key=folder_name)
                flash(f"Folder '{folder_name}' created successfully.", "success")
            except Exception as e:
                flash(f"Error: {str(e)}", "error")
        else:
            flash("Please enter a folder name.", "error")
        return redirect("/")
    return render_template("index.html")

# Запуск сервера
if __name__ == "__main__":
    app.run(debug=True)
