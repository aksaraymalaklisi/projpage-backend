import json
from google import genai
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from qdrant_client import AsyncQdrantClient, models
from .models import Message, ChatRoom
from django.contrib.auth.models import User
from channels.db import database_sync_to_async

# Initialize the GenAI Client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class ChatConsumer(AsyncWebsocketConsumer):
    
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        user = self.scope['user']

        if user.is_authenticated:
            # Save message to database
            room, _ = await database_sync_to_async(ChatRoom.objects.get_or_create)(name=self.room_name)
            message = await database_sync_to_async(Message.objects.create)(
                room=room,
                user=user,
                content=message_content
            )

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'user': user.username
                }
            )

            # Get response from Gemini
            bot_response = await self.get_gemini_response(message_content)

            # Save bot response to database
            bot_user, _ = await database_sync_to_async(User.objects.get_or_create)(username='chatbot')
            await database_sync_to_async(Message.objects.create)(
                room=room,
                user=bot_user,
                content=bot_response
            )

            # Send bot response to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': bot_response,
                    'user': 'chatbot'
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'error': 'Authentication required'
            }))

    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user
        }))

    async def get_gemini_response(self, user_message):
        try:
            # Use the Async Client
            qdrant_client = AsyncQdrantClient(host='qdrant', port=6333)

            #  Collection Check
            collection_name = "chatbot_memory"
            if not await qdrant_client.collection_exists(collection_name):
                await qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
                )

            # Generate embeddings
            embed_response = await client.aio.models.embed_content(
                model="text-embedding-004",
                contents=user_message
            )
            embedding = embed_response.embeddings[0].values

            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="is_knowledge",
                        match=models.MatchValue(value=True)
                    )
                ]
            )

            # Search the vector database
            search_response = await qdrant_client.query_points(
                collection_name=collection_name,
                query=embedding,
                limit=20, 
                query_filter=query_filter
            )
            search_result = search_response.points

            context = ""
            if search_result:
                for result in search_result:
                    context += result.payload['content'] + "\n"
                    
            system_instruction = (
                "Você é um assistente (chatbot) da página Green Trail. "
                "Responda o usuário utilizando apenas as informações dadas no contexto abaixo. "
                "Se essa informação não está no contexto, diga 'Não tenho essa informação.'"
            )

            prompt = f"""{system_instruction}\nContexto:\n{context}\n\nMensagem do usuário: {user_message}"""

            # Generate content
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            # 5. Store new memory using await and UUID for ID
            import uuid
            await qdrant_client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()), # Safer than using DB IDs
                        vector=embedding,
                        payload={"content": user_message},
                    )
                ],
                wait=True,
            )
            
            # Close the client connection nicely
            await qdrant_client.close()

            return response.text
        except Exception as e:
            print(f"!!! CHATBOT ERROR: {e} !!!")
            return f"An error occurred: {e}"