from django.contrib import admin, messages

from newsletter.utils.send_newsletters import send_email_newsletter

from .models import Newsletter, Category
from .utils.feeds import Feed


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["name"]}
    list_display = ('name', 'is_active', 'subscribers_num')
    readonly_fields = ('created_at',)
    
    actions = ('create_feed',)

    def create_feed(self, request, queryset):
        # This should always be overridden to use a task
        for obj in queryset:
            obj.rss_url = Feed().create_feed(obj.topic)
            obj.save()
        messages.add_message(
            request,
            messages.SUCCESS,
            'created google alert for (s) topics',
        )

    create_feed.short_description = 'Create feed alert'
    
    @admin.display(empty_value=0)
    def subscribers_num(self, obj):
        return len(obj.subscribers.all())
    

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["subject"]}
    date_hierarchy = 'created_at'
    list_display = (
        'subject', 'schedule', 'sent_at', 'created_at',
    )
    search_fields = ('subject',)
    readonly_fields = ('created_at', 'sent_at',)
    sortable_by = ('schedule', 'sent_at', 'created_at')

    actions = ('send_newsletters',)

    def send_newsletters(self, request, queryset):
        # This should always be overridden to use a task
        send_email_newsletter(newsletters=queryset, respect_schedule=False)
        messages.add_message(
            request,
            messages.SUCCESS,
            'Sending selected newsletters(s) to the subscribers',
        )
    
    send_newsletters.short_description = 'Send newsletters'
