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
    uploaded_file = request.files.get("file")
    
    if not uploaded_file or uploaded_file.filename == "":
        return "No file uploaded."

    file_ext = os.path.splitext(uploaded_file.filename)[1].lower()
    if file_ext not in [".csv", ".xlsx"]:
        return "Invalid file format. Please upload a CSV or XLSX file."

    try:
        # Read the file into a DataFrame
        uploaded_file.seek(0)  # Reset file pointer to start
        if file_ext == ".csv":
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')

        # Generate the profile report
        profile = ProfileReport(df, minimal=False)
        profile_file = "static/profile_report.html"
        profile.to_file(profile_file)
        
        return render_template("result.html", profile_url=f"/{profile_file}")
    
    except UnicodeDecodeError:
        try:
            uploaded_file.seek(0)  # Reset file pointer again
            df = pd.read_csv(uploaded_file, encoding='latin1')
            profile = ProfileReport(df, minimal=False)
            profile_file = "static/profile_report.html"
            profile.to_file(profile_file)
            return render_template("result.html", profile_url=f"/{profile_file}")
        except UnicodeDecodeError:
            return "Unable to read the file due to encoding issues."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

