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
        except Exception as e:
            return f"An error occurred while reading the file: {str(e)}"

        # Preprocess DataFrame if necessary
        # Example: Combining split columns if needed
        # df['Address'] = df['Address_Part1'].astype(str) + ' ' + df['Address_Part2'].astype(str)
        # df = df.drop(['Address_Part1', 'Address_Part2'], axis=1)

        # Generate the profile report
        try:
            profile = ProfileReport(df, minimal=False, explorative=True, correlations={"pearson": True})
            profile_file = "static/profile_report.html"
            profile.to_file(profile_file)
        except Exception as e:
            return f"An error occurred while generating the profile report: {str(e)}"

        return render_template("result.html", profile_url=f"/{profile_file}")
    else:
        return "No file uploaded."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
