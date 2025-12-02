import threading
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import KnowledgeBase, Document
from trackapp.models import Track
from .utils import sync_item_to_qdrant, delete_from_qdrant

# Debouncer
# This dictionary holds active timers: { 'model_name-id': TimerObject }
active_timers = {}
DELAY_SECONDS = 300 # Currently set to 5 minutes (leave it at 15 or so when testing)

def schedule_sync(instance):
    """
    Cancels existing timer for this specific object and starts a new one.
    """
    key = f"{instance._meta.model_name}-{instance.pk}"
    
    # Cancel existing timer if it's running
    if key in active_timers:
        active_timers[key].cancel()
    
    # Define the actual task
    def task():
        print(f"Timer finished. Syncing {key}...")
        sync_item_to_qdrant(instance)
        # Cleanup
        if key in active_timers:
            del active_timers[key]

    # Start new timer
    timer = threading.Timer(DELAY_SECONDS, task)
    active_timers[key] = timer
    timer.start()
    print(f"Scheduled sync for {key} in {DELAY_SECONDS}s")


# Signals
@receiver(post_save, sender=KnowledgeBase)
@receiver(post_save, sender=Document)
@receiver(post_save, sender=Track)
def on_save(sender, instance, created, **kwargs):
    # Get the list of fields being updated (if any)
    updated_fields = kwargs.get('update_fields') or []
    
    # Ignore list: If the save is ONLY for these internal fields, stop here.
    # This is necessary so that the auto-save logic doesn't apply to changes made by the auto-save itself.
    internal_fields = {'qdrant_id', 'processed'}
    
    if updated_fields and set(updated_fields).issubset(internal_fields):
        return

    # Trigger the debounce logic for actual content changes
    schedule_sync(instance)

@receiver(post_delete, sender=KnowledgeBase)
@receiver(post_delete, sender=Document)
@receiver(post_delete, sender=Track)
def on_delete(sender, instance, **kwargs):
    if instance.qdrant_id:
        delete_from_qdrant(instance.qdrant_id)