import requests
import fitz
import pyttsx3

def read_pdf_from_url(pdf_url):
    # Step 1: Download PDF from URL
    response = requests.get(pdf_url);
    if response.status_code != 200:
        print("Failed to Fetch PDF");
        return;
    # Step 2: Load PDF into Memory
    pdf_data = response.content
    pdf_doc = fitz.open(stream=pdf_data,filetype="pdf")
    
    # Step 3: Extract Data
    full_text = ""
    for page_num in range(len(pdf_doc)):
        page = pdf_doc[page_num]
        full_text += page.get_text()
        
    pdf_doc.close()
    return full_text

def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate',150)
    engine.setProperty('volume',0.9)
    engine.say(text)
    engine.runAndWait()

def read_text(url:str) -> dict:
    """Read out the PDF for User A user will provide the Link for PDF.
    
    Args:
        pdf_url: This will be the Link of the PDF
    
    """
    text = read_pdf_from_url(url)
    if text:
        print("reading the text ...")
        print(text[:100])
        speak_text(text[:1000])
    return {
            "status": "success",
            "report": f"Reading the first 1000 characters from the PDF at {url}"
        }
        
url = "https://pdfobject.com/pdf/sample.pdf"
text = read_text(url)
print(text)