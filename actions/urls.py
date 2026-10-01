from django.urls import path
from actions.views import (
    ActionRegisterView, MyActionItemsView, ActionDetailUpdateView,
    TriggerAIAnalysisView, MeetingAnalysisReportView, UnresolvedQuestionsListView
)

urlpatterns = [
    path('', ActionRegisterView.as_view(), name='action_register'),
    path('my/', MyActionItemsView.as_view(), name='my_action_items'),
    path('<int:pk>/', ActionDetailUpdateView.as_view(), name='action_detail_update'),
    path('transcripts/<int:transcript_id>/analyze/', TriggerAIAnalysisView.as_view(), name='trigger_ai_analysis'),
    path('meetings/<int:pk>/analysis/', MeetingAnalysisReportView.as_view(), name='meeting_analysis_report'),
    path('questions/', UnresolvedQuestionsListView.as_view(), name='unresolved_questions_list'),
    path('questions/<int:pk>/', UnresolvedQuestionsListView.as_view(), name='unresolved_question_detail'),
]
