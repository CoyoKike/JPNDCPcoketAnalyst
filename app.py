from flask import Flask, request, render_template
from pandas_profiling import ProfileReport
import pandas as pd
import os

app = Flask(__name__)

@app.route("/")
def upload_file():
    return render_template("upload.html")

@app.route("/process", methods=["POST"])
def process_file():
    uploaded_file = request.files["file"]
	@@ -21,10 +18,22 @@ def process_file():
            return "Invalid file format. Please upload a CSV or XLSX file."

        # Read the file into a DataFrame
        try:
            if file_ext == ".csv":
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            else:
                df = pd.read_excel(uploaded_file)
        except UnicodeDecodeError:
            # Try different encodings if UTF-8 fails
            try:
                uploaded_file.seek(0)  # Reset file pointer to start
                df = pd.read_csv(uploaded_file, encoding='latin1')
            except UnicodeDecodeError:
                try:
                    uploaded_file.seek(0)  # Reset file pointer to start
                    df = pd.read_csv(uploaded_file, encoding='iso-8859-1')
                except UnicodeDecodeError:
                    return "Unable to read the file due to encoding issues."

        # Generate the profile report
        profile = ProfileReport(df, minimal=True)
	@@ -35,6 +44,6 @@ def process_file():
    else:
        return "No file uploaded."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
