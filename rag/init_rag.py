"""
Initialization script for the RAG module.

This script initializes the RAG module with hotel information from text files.
"""

import os
import logging
import argparse
from typing import List, Tuple
import asyncio

from .rag_module import RAGModule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def load_hotel_info_files(directory: str) -> List[Tuple[str, str]]:
    """Load hotel information files.
    
    Args:
        directory: Directory containing hotel information files
        
    Returns:
        List of (filename, content) tuples
    """
    files = []
    
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")
        
        # Create a sample file if directory is empty
        sample_path = os.path.join(directory, "sample_hotel_info.txt")
        with open(sample_path, "w") as f:
            f.write("""
            Hotel Paradise Resort Information
            
            Check-in and Check-out:
            - Check-in time: 3:00 PM
            - Check-out time: 11:00 AM
            - Early check-in and late check-out available upon request (fees may apply)
            - Photo ID and credit card required at check-in
            
            Room Information:
            - All rooms feature air conditioning, flat-screen TVs, and free Wi-Fi
            - Deluxe rooms include a balcony with ocean view
            - Suites include a separate living area and kitchenette
            - Accessible rooms available upon request
            
            Dining Options:
            - The Ocean View Restaurant: Open 7:00 AM - 10:00 PM, serving international cuisine
            - Poolside Bar: Open 10:00 AM - 8:00 PM, serving drinks and light snacks
            - Room service available 24/7
            
            Facilities:
            - Outdoor swimming pool: Open 7:00 AM - 9:00 PM
            - Fitness center: Open 6:00 AM - 10:00 PM
            - Spa: Open 9:00 AM - 8:00 PM (reservations recommended)
            - Business center: Open 24/7
            
            Policies:
            - No smoking in rooms (designated smoking areas available)
            - Pets not allowed (service animals exempt)
            - Cancellation policy: 48 hours notice required to avoid charges
            """)
        logger.info(f"Created sample hotel information file: {sample_path}")
    
    # Load files
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r") as f:
                content = f.read()
            files.append((filename, content))
    
    logger.info(f"Loaded {len(files)} hotel information files")
    return files

def main():
    """Initialize the RAG module with hotel information."""
    parser = argparse.ArgumentParser(description="Initialize RAG module with hotel information")
    parser.add_argument("--hotel-info-dir", default="../data/hotel_info", help="Directory containing hotel information files")
    parser.add_argument("--clear", action="store_true", help="Clear existing vector store before ingestion")
    
    args = parser.parse_args()
    
    # Create RAG module
    rag_module = RAGModule()
    
    # Clear vector store if requested
    if args.clear:
        rag_module.vector_store.clear()
        logger.info("Cleared vector store")
    
    # Load hotel information files
    hotel_info_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), args.hotel_info_dir)
    files = load_hotel_info_files(hotel_info_dir)
    
    # Ingest hotel information
    total_chunks = 0
    for filename, content in files:
        source = os.path.splitext(filename)[0]
        chunks = rag_module.ingest_hotel_information(content, source=source)
        total_chunks += chunks
    
    logger.info(f"Ingested a total of {total_chunks} chunks from {len(files)} files")

if __name__ == "__main__":
    main()