from django.urls import path
from .views import root, data_table


urlpatterns = [
    path("", root, name="root"),
    path("data_table/", data_table, name="data_table")
]
