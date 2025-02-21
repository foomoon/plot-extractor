import os
import argparse
import fitz  # PyMuPDF


def extract(pdf_path, output_folder ="pdf"):
  
  # pdf_path = os.path.expanduser("~/Downloads/US8612008.pdf")
  doc = fitz.open(pdf_path)

  
  os.makedirs(output_folder, exist_ok=True)

  for page_number in range(len(doc)):
      page = doc[page_number]
      image_list = page.get_images(full=True)
      print(f"Page {page_number} has {len(image_list)} images.")

      for img_index, img in enumerate(image_list):
          xref = img[0]
          pix = fitz.Pixmap(doc, xref)
          # Check if image is CMYK; if so, convert to RGB
          if pix.n >= 5:
              pix = fitz.Pixmap(fitz.csRGB, pix)
          output_path = f"{output_folder}/extracted_image_{page_number}_{img_index}.png"
          pix.save(output_path)
          pix = None
          print(f"Saved {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PDF image extraction with command line settings.")
    parser.add_argument("--path", type=str,  help="Path to the input PDF.")
    parser.add_argument("--output", type=str, default="pdf", help="Path to the save extracted images.")
    args = parser.parse_args()

    path = args.path

    pdf_path = os.path.expanduser(args.path)

    print(pdf_path)
    extract(pdf_path, args.output)