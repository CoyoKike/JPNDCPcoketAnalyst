from flask import Flask, request, render_template
from pandas_profiling import ProfileReport
import pandas as pd
import os
import chardet

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
            uploaded_file.seek(0)  # Reset file pointer to start
            if file_ext == ".csv":
                # Detect file encoding
                result = chardet.detect(uploaded_file.read())
                encoding = result['encoding']
                uploaded_file.seek(0)  # Reset file pointer again
                df = pd.read_csv(uploaded_file, encoding=encoding)
            else:
                df = pd.read_excel(uploaded_file, engine='openpyxl')

        except UnicodeDecodeError as e:
            return f"Encoding error: {str(e)}"
        except Exception as e:
            return f"An error occurred while reading the file: {str(e)}"

        # Generate the profile report
        try:
            profile = ProfileReport(df, minimal=False)
            profile_file = "static/profile_report.html"
            profile.to_file(profile_file)
        except Exception as e:
            return f"An error occurred while generating the profile report: {str(e)}"

        return render_template("result.html", profile_url=f"/{profile_file}")
    else:
        return "No file uploaded."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
