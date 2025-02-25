@echo off
cd /d "A:\AI Intern\Intern\Cv_Analysis_app"
call venv\Scripts\activate
start "" http://localhost:8502
streamlit run app.py
