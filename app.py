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
    if uploaded_file.filename != "":
        file_ext = os.path.splitext(uploaded_file.filename)[1]
        if file_ext not in [".csv", ".xlsx"]:
            return "Invalid file format. Please upload a CSV or XLSX file."

        # Read the file into a DataFrame
        try:
            if file_ext == ".csv":
                df = pd.read_csv(uploaded_file, encoding='utf-8', quotechar='"')
            else:
                df = pd.read_excel(uploaded_file)
        except UnicodeDecodeError:
            # Try different encodings if UTF-8 fails
            try:
                uploaded_file.seek(0)  # Reset file pointer to start
                df = pd.read_csv(uploaded_file, encoding='latin1', quotechar='"')
            except UnicodeDecodeError:
                try:
                    uploaded_file.seek(0)  # Reset file pointer to start
                    df = pd.read_csv(uploaded_file, encoding='iso-8859-1', quotechar='"')
                except UnicodeDecodeError:
                    return "Unable to read the file due to encoding issues."

        # Convert currency columns to numeric (if needed)
        for col in df.columns:
            if df[col].dtype == 'object':
                # Remove common currency symbols and commas, then convert to numeric
                df[col] = df[col].replace({'\$': '', ',': ''}, regex=True)
                df[col] = pd.to_numeric(df[col], errors='ignore')

        # Generate the profile report
        profile = ProfileReport(df, minimal=False)
        profile_file = "static/profile_report.html"
        profile.to_file(profile_file)

        return render_template("result.html", profile_url=f"/{profile_file}")
    else:
        return "No file uploaded."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


