import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
def configure_api():
    """Configure the API key from environment variables, secrets, or user input"""
    # Try getting from user input in session state first
    if 'user_api_key' in st.session_state and st.session_state.user_api_key:
        api_key = st.session_state.user_api_key
    else:
        try:
            # Try getting from Streamlit secrets
            api_key = st.secrets["GEMINI_API_KEY"]
        except:
            # Fallback to environment variable
            api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(25.4, 12, 25.4)
        self.set_auto_page_break(auto=True, margin=25.4)
        
    def header(self):
        pass
    
    def footer(self):
        pass

def generate_ai_abstract(title):
    """Generate abstract using Gemini AI"""
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""Generate a single paragraph abstract for a research paper titled "{title}".
    The abstract should follow this structure:
    1. Introduction about current scenario and problem identification
    2. One sentence about current scenario
    3. Problem statement
    4. Solution method and challenges
    5. System objective (one sentence)
    6. Technologies used
    7. System advantages (time, cost benefits)
    8. Conclusion
    
    Keep it concise and academic. End with 3-4 relevant keywords if applicable.
    """
    
    response = model.generate_content(prompt)
    return response.text

def create_pdf(title, abstract, authors):
    """Create PDF with given title, abstract, and authors"""
    pdf = PDF()
    pdf.add_page()
    
    line_height = 7.5
    
    # Title
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, line_height, txt=title.upper(), ln=True, align='C')
    pdf.ln(2)
    
    # Abstract header
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, line_height, txt="Abstract", ln=True, align='C')
    pdf.ln(2)
    
    # Abstract content
    pdf.set_font('Times', '', 12)
    abstract = ' '.join(abstract.split())
    pdf.multi_cell(0, line_height, txt=abstract, align='J')
    
    pdf.ln(10)
    
    # Authors section
    pdf.set_font('Times', '', 12)
    max_width = 0
    lines = ["Prepared By,"] + [author.strip() + "," for author in authors if author.strip()]
    
    for line in lines:
        width = pdf.get_string_width(line)
        max_width = max(max_width, width)
    
    x_position = pdf.w - pdf.r_margin - max_width
    
    for line in lines:
        pdf.set_x(x_position)
        pdf.cell(max_width, line_height, txt=line, ln=True, align='L')
    
    return pdf.output(dest='S').encode('latin1')

def main():
    st.title("Abstract PDF Generator")
    
    # Add API key input in sidebar
    with st.sidebar:
        st.header("Settings")
        use_own_key = st.checkbox("Use your own API key")
        if use_own_key:
            api_key = st.text_input("Enter your Gemini API Key", type="password")
            st.session_state.user_api_key = api_key
            st.markdown("""
            ### How to get API Key:
            1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Create or select a project
            3. Generate an API key
            4. Copy and paste it here
            """)
        else:
            st.session_state.user_api_key = None
    
    # Configure API
    api_configured = configure_api()
    if not api_configured:
        st.error("API configuration error. Please contact the administrator or use your own API key.")
        return
    
    # Input fields
    title = st.text_input("Document Title", "")
    
    # Default authors
    default_authors = [
        "Adithya Raj",
        "Lidiya Reju",
        "Jibin Gigi",
        "Manu Emmanuel",
        "S6 CS A"
    ]
    
    # Author inputs
    st.subheader("Authors")
    authors = []
    for i, default_author in enumerate(default_authors):
        author = st.text_input(f"Author {i+1}", value=default_author)
        authors.append(author)
    
    # Add tabs for different abstract input methods
    tab1, tab2 = st.tabs(["Manual Input", "AI Generated"])
    
    with tab1:
        abstract = st.text_area("Abstract", "", height=200)
        if st.button("Generate PDF"):
            if title and abstract and any(authors):
                try:
                    pdf_bytes = create_pdf(title, abstract, authors)
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=f"{title.lower().replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("PDF generated successfully!")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Please fill in all required fields (Title, Abstract, and at least one Author).")
    
    with tab2:
        generate_button = st.button("Generate with AI")
        if generate_button:
            if not title:
                st.warning("Please enter a title first.")
            else:
                try:
                    with st.spinner("Generating abstract..."):
                        generated_abstract = generate_ai_abstract(title)
                        st.session_state.generated_abstract = generated_abstract
                        st.text_area("Generated Abstract", generated_abstract, height=200)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            # Download abstract as text
                            st.download_button(
                                label="Download Abstract as TXT",
                                data=generated_abstract,
                                file_name=f"{title.lower().replace(' ', '_')}_abstract.txt",
                                mime="text/plain"
                            )
                        
                        with col2:
                            # Download as PDF
                            if any(authors):
                                pdf_bytes = create_pdf(title, generated_abstract, authors)
                                st.download_button(
                                    label="Download as PDF",
                                    data=pdf_bytes,
                                    file_name=f"{title.lower().replace(' ', '_')}.pdf",
                                    mime="application/pdf"
                                )
                            else:
                                st.warning("Please fill in at least one author for PDF generation.")
                                
                except Exception as e:
                    st.error(f"Error generating abstract: {str(e)}")

if __name__ == "__main__":
    main()
