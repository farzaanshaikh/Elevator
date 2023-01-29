from django.urls import path

from . import views

urlpatterns = [
    path('building/', views.BuildingView.as_view()),
    path('elevator/', views.ElevatorView.as_view()),
    path('move/', views.ElevatorMoveView.as_view()),
    path('logs/', views.ElevatorLogsView.as_view()),
]