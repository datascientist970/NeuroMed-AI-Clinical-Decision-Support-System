from django.urls import path
from .views import ClinicalDecisionSupportAPIView, home

urlpatterns = [
    path(
        "clinical-support/",
        ClinicalDecisionSupportAPIView.as_view(),
        name="clinical-support"
    ),
    path('', home, name='home'),
]
