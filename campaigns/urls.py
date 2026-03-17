from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, LeadViewSet, LeadDraftViewSet, CampaignWorkflowStepViewSet

router = DefaultRouter()
router.register(r'list', CampaignViewSet, basename='campaign')
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'drafts', LeadDraftViewSet, basename='leaddraft')
router.register(r'steps', CampaignWorkflowStepViewSet, basename='workflowstep')

urlpatterns = [
    path('', include(router.urls)),
]
