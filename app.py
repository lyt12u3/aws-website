from flask import Flask, render_template, request, redirect, flash, send_file, url_for
import boto3
import os
import io
from dotenv import load_dotenv

# Завантаження змінних середовища з .env
load_dotenv()

# Ініціалізація Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")
S3_BUCKET = "student-website-vbohuslavskyi-2025"

s3 = boto3.client("s3")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "create_folder" in request.form:
            folder_name = request.form.get("folder_name", "").strip()
            if folder_name:
                if not folder_name.endswith("/"):
                    folder_name += "/"
                try:
                    s3.put_object(Bucket=S3_BUCKET, Key=folder_name)
                    flash(f"Folder '{folder_name}' created successfully.", "success")
                except Exception as e:
                    flash(f"Error creating folder: {str(e)}", "error")
            else:
                flash("Please enter a folder name.", "error")

        elif "delete_object" in request.form:
            target_name = request.form.get("delete_name", "").strip()
            if target_name:
                try:
                    if not target_name.endswith("/"):
                        target_name = target_name + "/"
                    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=target_name)
                    if "Contents" in response:
                        to_delete = [{"Key": obj["Key"]} for obj in response["Contents"]]
                        s3.delete_objects(Bucket=S3_BUCKET, Delete={"Objects": to_delete})
                        flash(f"Folder '{target_name}' and its contents deleted.", "success")
                    else:
                        flash(f"No objects found with prefix '{target_name}'.", "info")
                except Exception as e:
                    flash(f"Error deleting: {str(e)}", "error")
            else:
                flash("Please enter a file or folder name to delete.", "error")
        elif "upload_file" in request.form:
            file = request.files.get("file")
            folder_path = request.form.get("upload_path", "").strip()  # може бути пустим
            if file:
                filename = file.filename  # без secure_filename, як домовились
                if folder_path:
                    s3_key = f"{folder_path.rstrip('/')}/{filename}"
                else:
                    s3_key = filename  # завантажуємо просто у корінь бакету

                try:
                    s3.upload_fileobj(file, S3_BUCKET, s3_key)
                    flash(f"✅ File '{filename}' uploaded to '{s3_key}'", "success")
                except Exception as e:
                    flash(f"Error uploading file: {str(e)}", "error")
            else:
                flash("Please select a file to upload.", "error")
        if request.method == "POST":
            # 1. Видалення файлу
            delete_key = request.form.get("delete_key")
            if delete_key:
                try:
                    s3.delete_object(Bucket=S3_BUCKET, Key=delete_key)
                    flash(f"✅ File '{delete_key}' deleted from bucket.", "success")
                except Exception as e:
                    flash(f"❌ Error deleting file: {str(e)}", "error")
                return redirect(url_for("index"))
        return redirect("/")
    return render_template("index.html")

@app.route("/files")
def list_files():
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET)
        files = []
        if "Contents" in response:
            for obj in response["Contents"]:
                files.append(obj["Key"])
        return render_template("index.html", files=files)
    except Exception as e:
        flash(f"Error retrieving files: {str(e)}", "error")
        return redirect("/")

@app.route("/download/<path:key>")
def download_file(key):
    try:
        file_stream = io.BytesIO()
        s3.download_fileobj(S3_BUCKET, key, file_stream)
        file_stream.seek(0)
        return send_file(file_stream, as_attachment=True, download_name=key.split("/")[-1])
    except Exception as e:
        flash(f"Error downloading file: {str(e)}", "error")
        return redirect(url_for("index"))

# Запуск сервера
if __name__ == "__main__":
    app.run(debug=True)
