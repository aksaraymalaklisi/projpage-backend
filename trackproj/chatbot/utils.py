import mimetypes
import uuid
from django.conf import settings
from google import genai
from qdrant_client import QdrantClient, models
from .models import Document, KnowledgeBase
from trackapp.models import Track

# Sync clients for background tasks
client = genai.Client(api_key=settings.GEMINI_API_KEY)
qdrant_client = QdrantClient(host='qdrant', port=6333)
COLLECTION_NAME = "chatbot_memory"

def sync_item_to_qdrant(instance):
    """
    Reads a KnowledgeBase or Document instance, extracts text, 
    and UPSERTS it into Qdrant.
    """
    text_content = ""
    source_info = ""
    
    # Extract Text based on model type
    if isinstance(instance, KnowledgeBase):
        text_content = instance.content
        source_info = f"Knowledge: {instance.title}"
    
    elif isinstance(instance, Document):
        file_path = instance.file.path
        mime_type, _ = mimetypes.guess_type(file_path)
        source_info = f"Document: {instance.title}"
        
        # Handle PDFs via Gemini
        # We should probably create .env entries to allow changing the model through there.
        # This would also require refactoring the code to allow models from other SDKS (like OpenAI).
        if mime_type == 'application/pdf':
            try:
                uploaded_file = client.files.upload(file=file_path)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[uploaded_file, "Transcribe the full text."]
                )
                text_content = response.text
                client.files.delete(name=uploaded_file.name)
            except Exception as e:
                print(f"Error reading PDF: {e}")
                return
        # Handle text files
        # Could also be handled by Gemini, especially if it contains OCR-only information.
        elif mime_type and mime_type.startswith('text'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
    
    elif isinstance(instance, Track):
        source_info = f"Track: {instance.label}"
        
        # We construct a natural language sentence so Gemini understands the context
        # since we store the difficulty as "facil", for code, and "Fácil", for readability.
        difficulty = instance.get_difficulty_display()
        route = instance.get_route_type_display() # Same goes for route types
        
        # Handle optional fields safely
        dist = f"{instance.distance} meters" if instance.distance else "Unknown distance"
        dur = f"{instance.duration} minutes" if instance.duration else "Unknown duration"
        elev = f"{instance.elevation} meters" if instance.elevation else "Unknown elevation"
        
        text_content = (
            f"Hiking Trail Name: {instance.label}.\n"
            f"Difficulty Level: {difficulty}.\n"
            f"Route Type: {route}.\n"
            f"Total Distance: {dist}.\n"
            f"Estimated Duration: {dur}.\n"
            f"Elevation Gain: {elev}.\n"
            f"Description: {instance.description}"
        )

    # Vectorize and upsert
    if text_content:
        # Generate new UUID if not exists, or use existing to overwrite
        if not instance.qdrant_id:
            instance.qdrant_id = uuid.uuid4()
            instance.save(update_fields=['qdrant_id'])
            
        # Get Embedding
        # !!! We should probably break the file in chunks in case it's too big.
        try:
            embed_response = client.models.embed_content(
                model="text-embedding-004",
                contents=text_content[:9000] # Simple truncate for safety
            )
            embedding = embed_response.embeddings[0].values

            qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=str(instance.qdrant_id),
                    vector=embedding,
                    payload={
                        "content": text_content,
                        "source": source_info,
                        "is_knowledge": True
                        }
                    )
                ]
            )
            print(f"Synced to Qdrant: {source_info}")
            
            if isinstance(instance, Document):
                instance.processed = True
                instance.save(update_fields=['processed'])

        except Exception as e:
            print(f"Error syncing to Qdrant: {e}")

def delete_from_qdrant(qdrant_id):
    """
    Deletes a specific point from Qdrant using the UUID.
    """
    if qdrant_id:
        try:
            qdrant_client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=models.PointIdsList(
                    points=[str(qdrant_id)]
                )
            )
            print(f"Deleted vector ID {qdrant_id}")
        except Exception as e:
            print(f"Error deleting from Qdrant: {e}")