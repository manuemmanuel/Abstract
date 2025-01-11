import streamlit as st
from fpdf import FPDF

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Set margins: left, top, right in mm (1 inch = 25.4 mm)
        self.set_margins(25.4, 12, 25.4)
        # Set auto page break with margin
        self.set_auto_page_break(auto=True, margin=25.4)
        
    def header(self):
        # Empty header
        pass
    
    def footer(self):
        # Empty footer
        pass

def create_pdf(title, abstract, authors):
    pdf = PDF()
    pdf.add_page()
    
    # Set line height for 1.5 spacing (default is 5, so 7.5 gives us 1.5 spacing)
    line_height = 7.5
    
    # Title - 14pt, Bold, Centered
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, line_height, txt=title.upper(), ln=True, align='C')
    # Reduced spacing between title and "Abstract" from 10 to 5
    pdf.ln(2)
    
    # Abstract header - 12pt, Bold, Centered
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, line_height, txt="Abstract", ln=True, align='C')
    pdf.ln(2)
    
    # Abstract content - 12pt, Regular, Justified
    pdf.set_font('Times', '', 12)
    
    # Clean up the abstract text - remove multiple spaces and line breaks
    abstract = ' '.join(abstract.split())
    
    # Use multi_cell with justified alignment and proper line height
    pdf.multi_cell(0, line_height, txt=abstract, align='J')
    
    pdf.ln(10)
    
    # Right-aligned section
    pdf.set_font('Times', '', 12)
    
    # Calculate width of the longest line for right alignment
    max_width = 0
    lines = ["Prepared By,"] + [author.strip() + "," for author in authors if author.strip()]
    
    for line in lines:
        width = pdf.get_string_width(line)
        max_width = max(max_width, width)
    
    # Calculate x position for right alignment
    x_position = pdf.w - pdf.r_margin - max_width
    
    # Print each line right-aligned
    for line in lines:
        pdf.set_x(x_position)
        pdf.cell(max_width, line_height, txt=line, ln=True, align='L')
    
    return pdf.output(dest='S').encode('latin1')

def main():
    st.title("Abstract PDF Generator")
    
    # Input fields
    title = st.text_input("Document Title", "")
    abstract = st.text_area("Abstract", "", height=200)
    
    # Default authors
    default_authors = [
        "Adithya Raj",
        "Lidiya Reju",
        "Jibin Gigi",
        "Manu Emmanuel",
        "S6 CS A"
    ]
    
    # Author inputs with default values
    st.subheader("Authors")
    authors = []
    for i, default_author in enumerate(default_authors):
        author = st.text_input(f"Author {i+1}", value=default_author)
        authors.append(author)
    
    # Generate PDF button
    if st.button("Generate PDF"):
        if title and abstract and any(authors):
            try:
                pdf_bytes = create_pdf(title, abstract, authors)
                
                # Create download button
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

if __name__ == "__main__":
    main()
