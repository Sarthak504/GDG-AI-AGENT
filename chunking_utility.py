
from typing import List, Dict
import re

class TextChunker:
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        # Store values
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        # Print info
        print("✨ TextChunker initialized!")
        print(f"   Chunk size: {chunk_size} words")
        print(f"   Overlap: {overlap} words")
        print(f"   Strategy: Preserve context with intelligent overlap")
    
    def split_into_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        clean_sentences = [s.strip() for s in sentences if s.strip()]
        return clean_sentences
    
    def count_words(self, text: str) -> int:
        return len(text.split())
    
    def chunk_by_words(self, text: str) -> List[Dict]:
        words = text.split()
        chunks = []
        chunk_id = 0
        start = 0
        
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'start_word': start,
                'end_word': end,
                'word_count': len(chunk_words),
                'method': 'word-based'
            })
            
            chunk_id += 1
            start = end - self.overlap
            
            if start <= chunks[-1]['start_word']:
                break
        
        return chunks
    
    def chunk_by_sentences(self, text: str) -> List[Dict]:
        sentences = self.split_into_sentences(text)
        chunks = []
        current_chunk = []
        current_word_count = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence_word_count = self.count_words(sentence)
            
            if current_word_count + sentence_word_count > self.chunk_size and current_chunk:
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': ' '.join(current_chunk),
                    'sentence_count': len(current_chunk),
                    'word_count': current_word_count,
                    'method': 'sentence-based'
                })
                
                overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                current_chunk = overlap_sentences
                current_word_count = sum(self.count_words(s) for s in current_chunk)
                chunk_id += 1
            
            current_chunk.append(sentence)
            current_word_count += sentence_word_count
        
        if current_chunk:
            chunks.append({
                'chunk_id': chunk_id,
                'text': ' '.join(current_chunk),
                'sentence_count': len(current_chunk),
                'word_count': current_word_count,
                'method': 'sentence-based'
            })
        
        return chunks
    
    def chunk_text(self, text: str, method: str = 'sentences') -> List[Dict]:
        if method == 'words':
            return self.chunk_by_words(text)
        elif method == 'sentences':
            return self.chunk_by_sentences(text)
        else:
            raise ValueError("Method must be 'words' or 'sentences'")
    
    def get_chunk_stats(self, chunks: List[Dict]) -> Dict:
        if not chunks:
            return {'error': 'No chunks provided'}
        
        word_counts = [chunk['word_count'] for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'avg_words_per_chunk': sum(word_counts) / len(word_counts),
            'min_words': min(word_counts),
            'max_words': max(word_counts),
            'total_words': sum(word_counts),
            'method': chunks[0].get('method', 'unknown')
        }


# DEMO
if __name__ == "__main__":
    sample_text = """
    Artificial Intelligence is transforming the world. 
    Machine learning allows computers to learn from data.
    Deep learning uses neural networks.
    NLP helps computers understand language.
    Computer vision helps machines see.
    AI will shape the future.
    """

    chunker = TextChunker(chunk_size=20, overlap=5)

    print("\nSentence based chunking:\n")
    chunks = chunker.chunk_text(sample_text, method='sentences')
    for c in chunks:
        print(c)

    print("\nStats:")
    print(chunker.get_chunk_stats(chunks))
