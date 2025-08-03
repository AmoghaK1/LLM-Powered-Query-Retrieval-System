import fitz  # PyMuPDF
import pymupdf  # PyMuPDF
import pdfplumber
import pandas as pd
import os

# Create directories for organized output
os.makedirs("extracted_tables", exist_ok=True)
os.makedirs("extracted_images", exist_ok=True)
os.makedirs("extracted_text", exist_ok=True)

pdf_path = "pdf-extract\\Arogya Sanjeevani Policy.pdf"

# === TEXT EXTRACTION (Your existing code) ===
print("Extracting text...")
doc = fitz.open(pdf_path)
out = open("extracted_text\\output.txt", "wb")
for page in doc:
    text = page.get_text().encode("utf8")
    out.write(text)
    out.write(bytes((12,)))
out.close()
print("Text extraction completed!")

# === IMAGE EXTRACTION (Your existing code with improvements) ===
print("Extracting images...")
for page_index in range(len(doc)):
    page = doc[page_index]
    image_list = page.get_images()

    if image_list:
        print(f"Found {len(image_list)} images on page {page_index}")
    else:
        print("No images found on page", page_index)

    for image_index, img in enumerate(image_list, start=1):
        xref = img[0]
        pix = pymupdf.Pixmap(doc, xref)

        if pix.n - pix.alpha > 3:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

        pix.save(f"extracted_images\\page_{page_index}_image_{image_index}.png")
        pix = None

print("Image extraction completed!")

# === TABLE EXTRACTION using pdfplumber ===
print("Extracting tables...")
with pdfplumber.open(pdf_path) as pdf:
    all_tables_data = []
    
    for page_num, page in enumerate(pdf.pages):
        print(f"Processing page {page_num + 1}...")
        
        # Extract tables from current page
        tables = page.extract_tables()
        
        if tables:
            print(f"Found {len(tables)} tables on page {page_num + 1}")
            
            for table_num, table in enumerate(tables):
                if table and len(table) > 0:
                    # Create DataFrame
                    if len(table) > 1:
                        # Use first row as headers if it looks like headers
                        df = pd.DataFrame(table[1:], columns=table[0])
                    else:
                        df = pd.DataFrame(table)
                    
                    # Clean up the data (remove None values)
                    df = df.fillna("")
                    
                    # Save individual table
                    table_filename = f"extracted_tables\\page_{page_num + 1}_table_{table_num + 1}.csv"
                    df.to_csv(table_filename, index=False, encoding='utf-8')
                    
                    # Also save as Excel for better formatting
                    excel_filename = f"extracted_tables\\page_{page_num + 1}_table_{table_num + 1}.xlsx"
                    df.to_excel(excel_filename, index=False)
                    
                    # Store table info
                    table_info = {
                        'page': page_num + 1,
                        'table_num': table_num + 1,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'filename': table_filename
                    }
                    all_tables_data.append(table_info)
                    
                    print(f"  Table {table_num + 1}: {len(df)} rows × {len(df.columns)} columns")
        else:
            print(f"No tables found on page {page_num + 1}")

# Create summary of extracted tables
if all_tables_data:
    summary_df = pd.DataFrame(all_tables_data)
    summary_df.to_csv("extracted_tables\\tables_summary.csv", index=False)
    print(f"\nTotal tables extracted: {len(all_tables_data)}")
    print("Table summary saved to: extracted_tables\\tables_summary.csv")
else:
    print("No tables found in the PDF")

doc.close()
print("\nExtraction completed! Check the following directories:")
print("- extracted_text\\ for text files")
print("- extracted_images\\ for image files")
print("- extracted_tables\\ for table files")