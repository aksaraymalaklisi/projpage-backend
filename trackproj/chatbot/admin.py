from django.contrib import admin
from django.contrib import messages
from .models import ChatRoom, Message, KnowledgeBase, Document

from .utils import sync_item_to_qdrant

def force_sync_action(modeladmin, request, queryset):
    """
    Action to manually force an update to Qdrant, skipping the delay.
    """
    success_count = 0
    error_count = 0

    for item in queryset:
        try:
            # Call the util function directly (bypassing signals/timers)
            sync_item_to_qdrant(item)
            success_count += 1
        except Exception as e:
            error_count += 1
            modeladmin.message_user(request, f"Error syncing {item}: {e}", messages.ERROR)

    if success_count > 0:
        modeladmin.message_user(request, f"Successfully forced sync for {success_count} items.", messages.SUCCESS)

force_sync_action.short_description = "Force Update Vector DB (Skip Delay)"

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'content', 'timestamp')
    list_filter = ('room', 'user')
    search_fields = ('content',)

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'qdrant_id')
    search_fields = ('title', 'content')
    # Add the manual button to the actions dropdown
    actions = [force_sync_action]

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'processed', 'qdrant_id')
    search_fields = ('title',)
    readonly_fields = ('processed', 'qdrant_id')
    actions = [force_sync_action]