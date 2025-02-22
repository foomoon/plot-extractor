import os
import argparse
import fitz  # PyMuPDF
import re

def remove_repeated_underscores(s):
    return re.sub(r'_{2,}', '_', s)


def extract(pdf_path, output_folder ="pdf", max_file_length=100):
  
  figure_keywords = ["Figure", "Table", "FIGURE", "TABLE", "FIG", "fig", "figure", "table"]
  
  doc = fitz.open(pdf_path)

  total_images_saved = 0

  os.makedirs(output_folder, exist_ok=True)

  for page_number in range(len(doc)):
      page = doc[page_number]
      image_list = page.get_images(full=True)
      images_per_page = len(image_list) 
      text_blocks = page.get_text("dict")["blocks"]
      print(f"Page {page_number+1} has {images_per_page} images and {len(text_blocks)} text blocks.")

      for img_index, img in enumerate(image_list):
          xref = img[0]
          rect = page.get_image_rects(xref)[0]
          image_text = get_closest_text_block(text_blocks, rect)
          # Check if text contains "Figure" or "Table" (or other keywords)
          if image_text and any(keyword in image_text for keyword in figure_keywords):
            # Get matched keyword
            #   keyword = next((keyword for keyword in figure_keywords if keyword in image_text), None)       
            figure_caption = image_text.replace("\n", " ").replace("  "," ").replace(" ", "_")
            # Remove special characters that can't be in filenames
            figure_caption = "".join(c for c in figure_caption if c.isalnum() or c in "_-")
            # Remove repeated underscores
            figure_caption = remove_repeated_underscores(figure_caption)
            # Limit caption length to 50 characters
            figure_caption = figure_caption[:max_file_length]
            
          else:
            figure_caption = "No_Cap"
        #   print(f"Image {page_number+1}.{img_index} with caption: {figure_caption}")
         
          pix = fitz.Pixmap(doc, xref)
          # Check if image is CMYK; if so, convert to RGB
          if pix.n >= 5:
              pix = fitz.Pixmap(fitz.csRGB, pix)
          output_path = f"{output_folder}/{page_number+1}_{img_index}_{figure_caption}.png"
          pix.save(output_path)
          pix = None
          print(f"[Saved] {output_path}")
          total_images_saved += 1

  print("\n-----------------------------------------")
  print(f"Total images saved: {total_images_saved}")
  print(f"Output path: {output_path}\n")

def get_closest_text_block(text_blocks, image_rect):
    """Get the text block closest to the image."""
    closest_distance = float("inf")
    closest_block = None
    for block in text_blocks:
        # Skip non-text blocks (or blocks without "lines")
        if block.get("type", 1) != 0 or "lines" not in block:
            continue

        bbox = block["bbox"]
        block_rect = fitz.Rect(bbox)
        distance = block_rect.tl.distance_to(image_rect.bl)
        if distance < closest_distance:
            closest_distance = distance
            closest_block = block

    # Extract text from the closest block (if found)
    if closest_block:
        text = ""
        for line in closest_block["lines"]:
            span_text = " ".join(span["text"] for span in line["spans"])
            text += span_text + "\n"
        return text
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PDF image extraction with command line settings.")
    parser.add_argument("--p", type=str,  help="Path to the input PDF.")
    parser.add_argument("--o", type=str, default="pdf", help="Path to the save extracted images.")
    parser.add_argument("--l", type=int, default=100, help="Maximum length of the filename.")
    
    args = parser.parse_args()
    pdf_path = os.path.expanduser(args.p)

    print(pdf_path)
    extract(pdf_path, args.o, args.l)