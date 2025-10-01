from django.urls import path

from movies.api.v1 import views

urlpatterns = [
    path('movies/', views.FilmWorkListApi.as_view()),
    path('movies/<uuid:pk>/', views.FilmWorkDetailApi.as_view())
]
