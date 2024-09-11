from flask import Flask, request, render_template
from pandas_profiling import ProfileReport
import pandas as pd
import os
from openpyxl import load_workbook
import openpyxl

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

        try:
            if file_ext == ".csv":
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            else:
                df = pd.read_excel(uploaded_file)
        except UnicodeDecodeError:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='latin1')
            except UnicodeDecodeError:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='iso-8859-1')
                except UnicodeDecodeError:
                    return "Unable to read the file due to encoding issues."
        except TypeError as e:
            return f"Error processing Excel file: {e}"
        except openpyxl.utils.exceptions.InvalidFileException:
            return "The Excel file format is not supported."

        # Replace spaces with underscores in categorical columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.replace(' ', '_')

        # Generate the profile report
        profile = ProfileReport(df, minimal=False)
        profile_file = "static/profile_report.html"
        profile.to_file(profile_file)

        return render_template("result.html", profile_url=f"/{profile_file}")
    else:
        return "No file uploaded."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

