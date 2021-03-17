from django.urls import path

from . import views

urlpatterns = [
    path('save/<slug:name>/', views.SaveView.as_view(), name='save'),
    path('list/', views.ListView.as_view(), name='list'),
    path('load/<slug:name>/', views.LoadView.as_view(), name='load'),
    path('delete/<slug:name>/', views.DeleteView.as_view(), name='delete'),
]
