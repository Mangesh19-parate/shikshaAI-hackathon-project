import sys
from pathlib import Path
import json

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from backend.api.services.retriever import HybridRetriever

# A small test set of questions we know are in NCERT
TEST_SET = [
    {
        "question": "What is photosynthesis?",
        "expected_keywords": ["chlorophyll", "sunlight", "carbon dioxide", "water"]
    },
    {
        "question": "Explain Ohm's Law.",
        "expected_keywords": ["potential difference", "current", "proportional", "resistance"]
    },
    {
        "question": "What are the main causes of the French Revolution?",
        "expected_keywords": ["louis xvi", "taxes", "estates", "bastille"]
    }
]

def calculate_precision_at_k(results, expected_keywords, k=5):
    """Simple precision calculation based on keyword presence in top k chunks."""
    if not results:
        return 0.0
        
    top_k = results[:k]
    relevant_count = 0
    
    for chunk in top_k:
        text = chunk['text'].lower()
        if any(kw.lower() in text for kw in expected_keywords):
            relevant_count += 1
            
    return relevant_count / k

def evaluate():
    retriever = HybridRetriever()
    print(f"Loaded retriever with collection: {retriever.collection_name}")
    
    total_p5 = 0.0
    
    for item in TEST_SET:
        question = item['question']
        expected_keywords = item['expected_keywords']
        
        results = retriever.retrieve(question, top_k=5)
        
        p5 = calculate_precision_at_k(results, expected_keywords, k=5)
        total_p5 += p5
        
        print(f"\nQuestion: {question}")
        print(f"Precision@5: {p5:.2f}")
        for idx, hit in enumerate(results[:2]):
            print(f"  Top {idx+1} Match: {hit['metadata'].get('textbook', 'Unknown')} (Score: {hit['score']:.4f})")
            
    avg_p5 = total_p5 / len(TEST_SET)
    print(f"\n=================================")
    print(f"Average Precision@5: {avg_p5:.2f}")
    print(f"=================================")
    
if __name__ == "__main__":
    evaluate()
