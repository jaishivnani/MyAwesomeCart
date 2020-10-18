from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path("",views.index, name="BlogHome"),
    path("blogpost/<int:id>",views.blogpost, name="blogHome"),
    path("blogpost/<int:id>",views.blogpost, name="blogHome"),



]