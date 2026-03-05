\# Resume AI SaaS


An AI-powered Resume Analyzer that evaluates resumes against job descriptions using Natural Language Processing (NLP) techniques. The system extracts text from PDF resumes, compares it with job descriptions using TF-IDF and cosine similarity, identifies skill matches, calculates an ATS compatibility score, and generates a detailed PDF analysis report.




\## Features



\* User Authentication (Signup \& Login)

\* Resume Upload (PDF)

\* Resume text extraction using PDF parsing

\* Skill detection and matching

\* TF-IDF similarity analysis

\* Cosine similarity job description matching

\* ATS score calculation

\* Resume improvement suggestions

\* Automatic PDF report generation



---



\## Tech Stack



\### Backend



\* Python

\* Flask

\* Flask-Login

\* Flask-SQLAlchemy



\### Machine Learning / NLP



\* Scikit-learn

\* TF-IDF Vectorizer

\* Cosine Similarity



\### Libraries



\* PDFPlumber

\* ReportLab

\* NumPy

\* SciPy



\### Database



\* SQLite



\### Frontend



\* HTML

\* CSS

\* JavaScript



---



\## Project Structure



```

resume-ai-SaaS

│

├── backend

│   ├── app.py

│   ├── templates

│   │   ├── index.html

│   │   ├── login.html

│   │   └── signup.html

│   │

│   ├── static

│   │   └── style.css

│   │

│   └── instance

│

├── requirements.txt

├── README.md

└── screenshots

```



---



\## Installation



Clone the repository



```

git clone https://github.com/SHiVaNsH2005-spec/resume-ai-SaaS.git

cd resume-ai-SaaS

```



Create a virtual environment



```

python -m venv venv

```



Activate the virtual environment
Windows: venv\\Scripts\\activate
 
Install dependencies:
pip install -r requirements.txt



Run the application:

python backend/app.py


Open your browser and visit:

http://127.0.0.1:5000



\## How the System Works



1\. User signs up or logs into the application.

2\. User uploads a resume in PDF format.

3\. The system extracts text from the PDF using PDFPlumber.

4\. Resume text and job description are normalized and processed.

5\. TF-IDF vectorization converts text into numerical vectors.

6\. Cosine similarity calculates similarity between resume and job description.

7\. Skills are detected using predefined keyword matching.

8\. Scores are calculated:



&nbsp;  \* Skill Score

&nbsp;  \* ATS Score

&nbsp;  \* Job Description Match Score

&nbsp;  \* Final Resume Score

9\. The system generates suggestions for improving the resume.

10\. A downloadable PDF report is generated with the analysis results.



\## Output Provided by the System



\* Resume Strength Label

\* Skills Score

\* ATS Compatibility Score

\* Cosine Similarity Score

\* Job Description Match Score

\* Matched Skills

\* Missing Skills

\* Improvement Suggestions

\* Downloadable PDF Resume Report




\## Future Improvements



\* Skill heatmap visualization

\* Resume keyword highlighting

\* Job role prediction using ML

\* Integration with job portals

\* Cloud deployment

\* Resume formatting analysis




\## Author

Shivansh Porwal



GitHub Profile

https://github.com/SHiVaNsH2005-spec



\## License
This project is created for educational and learning purposes.



