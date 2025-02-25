import streamlit as st
import pdfplumber
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama  
from langchain_core.runnables import RunnablePassthrough
import time

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        # Reset the file pointer to the beginning
        pdf_file.seek(0)
        
        # Ensure the file is not empty
        if pdf_file.size == 0:
            st.error("Uploaded file is empty. Please upload a valid PDF file.")
            return None
        
        # Read the file and extract text
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

# Function to analyze CV using Ollama and LangChain
def analyze_cv(cv_text, description, instructions):
    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["cv_text", "description", "instructions"],
        template="""
        Analyze the following CV based on the provided description and instructions:
        
        **Description**: {description}
        **Instructions**: {instructions}
        
        **CV Text**: {cv_text}
        
        Based on the above, provide a Recommended or Not Recommended no description or explanation.
        """
    )

    # Initialize the LLM with Ollama (using Mistral model)
    llm = Ollama(model="mistral")  

    # Create a chain using RunnablePassthrough
    chain = (
        RunnablePassthrough.assign(
            cv_text=lambda x: x["cv_text"],
            description=lambda x: x["description"],
            instructions=lambda x: x["instructions"],
        )
        | prompt_template
        | llm
    )

    # Run the chain
    result = chain.invoke({"cv_text": cv_text, "description": description, "instructions": instructions})
    return result

# Streamlit UI
st.title("CV Analyzer for Hiring")
st.write("Welcome to the CV Analysis Chatbot!")

# File uploader
uploaded_file = st.file_uploader("Upload CV", type="pdf")

# Debugging: Verify the uploaded file
if uploaded_file is not None:
    st.write("Uploaded file name:", uploaded_file.name)
    st.write("Uploaded file size:", uploaded_file.size)
    st.write("Uploaded file type:", uploaded_file.type)

    # Save the uploaded file temporarily for debugging
    with open("temp_uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.write("File saved temporarily. Verify if it opens correctly.")

    # Text extraction
    if uploaded_file.size == 0:
        st.error("Uploaded file is empty. Please upload a valid PDF file.")
    else:
        st.success("File uploaded successfully!")
        cv_text = extract_text_from_pdf(uploaded_file)
        if cv_text is not None:  # Ensure text extraction was successful
            st.write("Extracted Text from CV:")
            st.text_area("CV Text", cv_text, height=300)

# Input fields for description and instructions
description = st.text_area(
    "Hiring Description about CV",
    value="We are hiring for an Information Technology Technician with expertise in systems administration, network security, and cloud infrastructure. The ideal candidate should have strong experience in managing Microsoft Office 365, Azure, VMware, and enterprise backup systems. Proficiency in PowerShell, Active Directory, and disaster recovery planning is essential. The candidate should also possess excellent troubleshooting skills and a proven track record of managing IT infrastructure in a corporate environment."
)

instructions = st.text_area(
    "Instruction for CV",
    value="1. Check if the candidate has at least 5 years of experience in systems administration and network security. "
          "2. Verify if the candidate has hands-on experience with Microsoft Office 365, Azure, and VMware. "
          "3. Ensure the candidate has experience with enterprise backup systems and disaster recovery planning. "
          "4. Look for proficiency in PowerShell scripting and Active Directory management. "
          "5. Confirm that the candidate has a Bachelor's degree in Information Technology or a related field. "
          "6. Check for relevant certifications such as CompTIA Network+. "
          "7. If the candidate meets all the above criteria, recommend 'Recommended.' Otherwise, recommend 'Not Recommended.', Do not explain these seven points i need answer in one word Recommended or Not Recommended"
)

# Analyze button
if st.button("Analyze CV"):
    if uploaded_file is not None and description and instructions:
        if uploaded_file.size == 0:
            st.error("Uploaded file is empty. Please upload a valid PDF file.")
        else:
            with st.spinner("Analyzing CV..."):
                # Extract text from the uploaded CV
                cv_text = extract_text_from_pdf(uploaded_file)
                
                if cv_text is not None:  
                    # Analyze the CV using Ollama and LangChain
                    analysis_result = analyze_cv(cv_text, description, instructions) 
                    
                    # Simulate processing time (optional)
                    time.sleep(2)
                
                    # Display the result
                    st.write("Status:")
                    st.write(analysis_result)
    else:
        st.error("Please upload a CV for Analysis") 

# Clear button
if st.button("Clear"):
    uploaded_file = None
    description = ""
    instructions = ""
    st.write("Upload a new CV to analyze.")


