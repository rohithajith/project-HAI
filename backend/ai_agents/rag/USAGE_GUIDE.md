# RAG Module Usage Guide

This guide provides instructions for using the RAG (Retrieval Augmented Generation) module in the Hotel AI system.

## Installation

1. Install the required dependencies:

```bash
cd backend/ai_agents
pip install -r rag/requirements.txt
```

2. Initialize the RAG module with hotel information:

```bash
cd backend/ai_agents
python -m rag.init_rag --clear
```

This will load the hotel information from the `data/hotel_info` directory and create the vector database.

## API Endpoints

The RAG module is exposed through the following API endpoints:

### 1. Query Hotel Information

```
POST /api/hotel-info/query
```

Request body:
```json
{
  "message": "What time is check-in?",
  "history": [
    {
      "role": "user",
      "content": "Hello, I have a question about the hotel."
    },
    {
      "role": "system",
      "content": "Hello! How can I assist you with our hotel today?"
    }
  ],
  "guestName": "John Doe",
  "bookingId": "B12345",
  "queryType": "check_in_out"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "response": "Check-in time at our hotel is 3:00 PM. You'll need to bring a valid photo ID and the credit card used for the reservation. If you'd like to check in earlier, you can request early check-in, which may be available for an additional fee depending on room availability.",
    "suggested_actions": [
      "View check-in/out times",
      "Request early check-in",
      "Request late check-out"
    ],
    "related_info": {
      "category": "check_in_out",
      "highlights": [
        {
          "category": "policies",
          "content": "Check-in time: 3:00 PM, Check-out time: 11:00 AM, Early check-in and late check-out available upon request..."
        }
      ]
    }
  }
}
```

### 2. Initialize RAG Module (Admin Only)

```
POST /api/hotel-info/init-rag
```

Query parameters:
- `clear` (optional): Set to "true" to clear existing vector store before ingestion

Response:
```json
{
  "status": "success",
  "message": "RAG module initialized successfully",
  "details": "Loaded 2 hotel information files\nIngested a total of 25 chunks"
}
```

### 3. Get RAG Status

```
GET /api/hotel-info/rag-status
```

Response:
```json
{
  "status": "success",
  "data": {
    "initialized": true,
    "document_count": 25,
    "embedding_dimension": 768,
    "categories": {
      "rooms": 5,
      "dining": 4,
      "spa": 3,
      "facilities": 4,
      "policies": 6,
      "general": 3
    }
  }
}
```

## Adding Hotel Information

To add new hotel information:

1. Create a text file in the `backend/ai_agents/data/hotel_info` directory
2. Add the hotel information to the file
3. Reinitialize the RAG module using the API endpoint or the command-line script

Example hotel information file format:

```
Room Service Information

Hours:
- Available 24/7
- Full menu available from 6:00 AM to 11:00 PM
- Limited menu available from 11:00 PM to 6:00 AM

Menu Highlights:
- Breakfast: Continental, American, and Healthy options
- Lunch & Dinner: International cuisine, local specialties
- Beverages: Full bar service, premium wines, craft cocktails

Ordering:
- Dial extension 1234 from your room phone
- Order through the hotel app
- Order through the TV menu system

Delivery Time:
- Approximately 30-45 minutes during peak hours
- 20-30 minutes during off-peak hours

Special Requests:
- Dietary restrictions accommodated with advance notice
- Special occasion setups available (additional fee may apply)
- Private dining experience can be arranged through concierge
```

## Programmatic Usage

To use the RAG module programmatically in your own code:

```python
from rag.rag_module import RAGModule, RAGQuery

# Initialize the RAG module
rag_module = RAGModule()

# Process a query
async def process_query(query_text):
    result = await rag_module.process_query(RAGQuery(query=query_text))
    return result.context, result.documents

# Ingest new hotel information
def add_hotel_info(text, source="custom"):
    chunks = rag_module.ingest_hotel_information(text, source=source)
    return chunks
```

## Troubleshooting

If you encounter issues with the RAG module:

1. Check that all dependencies are installed
2. Verify that the vector database files exist in `backend/ai_agents/data/vector_db`
3. Check the logs for error messages
4. Try reinitializing the RAG module with the `--clear` flag
5. Ensure the hotel information files are properly formatted

For more detailed information, refer to the implementation notes and the code documentation.