from django.contrib import admin
from actions.models import Decision, ActionItem, UnresolvedQuestion, Dependency

@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'decision', 'confidence', 'created_at']

@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'task', 'owner_name', 'owner_user', 'deadline', 'priority', 'status']
    list_filter = ['status', 'priority']
    search_fields = ['task', 'owner_name', 'evidence']

@admin.register(UnresolvedQuestion)
class UnresolvedQuestionAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'question', 'status', 'resolved_by', 'created_at']
    list_filter = ['status']

@admin.register(Dependency)
class DependencyAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'description', 'created_at']
