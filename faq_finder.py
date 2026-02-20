"""
Day 1 - Exercise 3: Intelligent FAQ Finder [WORKBOOK]
======================================================
"""

import importlib
from typing import List, Dict

# Import our previous utilities
from text_cleaner import TextCleaner
from semantic_similarity import SemanticSimilarity


class FAQFinder:
    def __init__(self):

        # Initialize TextCleaner
        self.cleaner = TextCleaner()
        
        # Initialize SemanticSimilarity
        self.similarity = SemanticSimilarity()
        
        # Initialize empty FAQ list
        self.faqs = []
        
        self.stop_words = {
            'a', 'an', 'the', 'is', 'are', 'am', 'be', 'to', 'of', 'in', 
            'on', 'at', 'for', 'with', 'do', 'does', 'i', 'you', 'we', 
            'they', 'there', 'can', 'will', 'it', 'what', 'how', 'when', 'where'
        }
        
        self.synonyms = {
            'sign': ['register', 'signup', 'join', 'enroll'],
            'register': ['sign', 'signup', 'join', 'enroll'],
            'signup': ['sign', 'register', 'join', 'enroll'],
            'pay': ['fee', 'cost', 'price', 'money', 'charge'],
            'fee': ['pay', 'cost', 'price', 'money', 'charge'],
            'cost': ['pay', 'fee', 'price', 'money', 'charge'],
            'start': ['schedule', 'time', 'begin', 'when'],
            'time': ['schedule', 'start', 'when'],
            'when': ['time', 'schedule', 'start'],
            'where': ['venue', 'location', 'place'],
            'venue': ['where', 'location', 'place'],
            'location': ['where', 'venue', 'place']
        }
        
        print("[OK] FAQ Finder initialized with smart matching!")
    
    def add_faq(self, question: str, answer: str):
        self.faqs.append({
            'question': question,
            'answer': answer,
            'question_clean': self.cleaner.clean_text(question)
        })
    
    def load_from_file(self, filepath: str):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and '|' in line:
                        question, answer = line.split('|', 1)
                        self.add_faq(question.strip(), answer.strip())
            
            print(f"✅ Loaded {len(self.faqs)} FAQs from {filepath}")
        except FileNotFoundError:
            print(f"❌ File not found: {filepath}")
        except Exception as e:
            print(f"❌ Error loading file: {e}")
    
    def expand_with_synonyms(self, words: set) -> set:
        expanded = set(words)
        
        for word in words:
            if word in self.synonyms:
                expanded.update(self.synonyms[word])
        
        return expanded
    
    def find_answer(self, user_question: str, threshold: float = 0.15) -> Dict:

        if not self.faqs:
            return {
                'answer': "❌ No FAQs loaded yet! Please add some FAQs first.",
                'confidence': 0.0,
                'matched_question': None
            }
        
        # Step 1: Clean user question
        user_clean = self.cleaner.clean_text(user_question)
        
        # Step 2: Remove stop words
        user_words_raw = set(user_clean.split()) - self.stop_words
        
        # Step 3: Expand synonyms
        user_words = self.expand_with_synonyms(user_words_raw)
        
        if not user_words:
            user_words = set(user_clean.split())
        
        best_match = None
        best_score = 0.0
        
        for faq in self.faqs:
            faq_words_raw = set(faq['question_clean'].split()) - self.stop_words
            faq_words = self.expand_with_synonyms(faq_words_raw)
            
            if not faq_words:
                faq_words = set(faq['question_clean'].split())
            
            # Jaccard similarity
            intersection = user_words.intersection(faq_words)
            union = user_words.union(faq_words)
            
            if len(union) > 0:
                score = len(intersection) / len(union)
            else:
                score = 0.0
            
            if score > best_score:
                best_score = score
                best_match = faq
        
        if best_score < threshold:
            return {
                'answer': "I couldn't find a good answer to that question. Could you rephrase it?",
                'confidence': best_score,
                'matched_question': None
            }
        
        return {
            'answer': best_match['answer'],
            'confidence': best_score,
            'matched_question': best_match['question']
        }


# DEMO
if __name__ == "__main__":
    finder = FAQFinder()

    finder.add_faq("How do I register for the event?", "Go to website and click register")
    finder.add_faq("Is there any fee?", "No, event is free")
    finder.add_faq("Where is the venue?", "At Tech Hub Innovation Center")

    while True:
        q = input("\nAsk question (type 'exit' to stop): ")
        if q.lower() == "exit":
            break
        
        result = finder.find_answer(q)
        print("\nMatched Question:", result['matched_question'])
        print("Confidence:", round(result['confidence'], 2))
        print("Answer:", result['answer'])
