import os
import sys
import fitz  # PyMuPDF
from pathlib import Path

# Add project root to Python path so we can import backend modules
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from backend.api.services.retriever import HybridRetriever

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Chunk text by characters with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def extract_metadata_from_filename(filename: str):
    """
    Extract class and subject from filename if possible.
    Example: Class_10_Science.pdf
    """
    parts = filename.replace('.pdf', '').split('_')
    meta = {
        "textbook": filename,
        "class": "Unknown",
        "subject": "Unknown",
        "chapter": "Unknown"
    }
    if len(parts) >= 3:
        meta["class"] = f"Class {parts[1]}"
        meta["subject"] = parts[2]
    return meta

def ingest_pdfs(pdf_dir: str):
    pdf_path = Path(pdf_dir)
    if not pdf_path.exists() or not pdf_path.is_dir():
        print(f"Directory {pdf_dir} does not exist.")
        return

    retriever = HybridRetriever()
    all_chunks = []

    print(f"Scanning {pdf_dir} for PDFs...")
    for file_path in pdf_path.glob("*.pdf"):
        print(f"Processing {file_path.name}...")
        meta = extract_metadata_from_filename(file_path.name)
        
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text").strip()
                if not text:
                    continue
                
                # Chunk the page text
                text_chunks = chunk_text(text)
                for chunk in text_chunks:
                    chunk_meta = meta.copy()
                    chunk_meta["page"] = page_num + 1
                    all_chunks.append({
                        "text": chunk,
                        "metadata": chunk_meta
                    })
        except Exception as e:
            print(f"Failed to process {file_path.name}: {e}")

    print(f"Extracted {len(all_chunks)} chunks total.")
    if all_chunks:
        print("Indexing into Qdrant and building BM25...")
        retriever.index_documents(all_chunks)
        print("Ingestion complete.")
    else:
        print("No text found to ingest.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest NCERT PDFs into the RAG vector DB.")
    parser.add_argument("--pdf-dir", type=str, default="data/ncert_pdfs", help="Directory containing the PDFs")
    args = parser.parse_args()
    
    ingest_pdfs(args.pdf_dir)
