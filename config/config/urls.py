from django.contrib import admin
from django.urls import path, include
from clinical.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("clinical.urls")),
    path("",home,name="home")
]
