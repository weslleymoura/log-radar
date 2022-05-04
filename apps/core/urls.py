from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('add-data-point/<str:origin>/<str:destination>/', views.add_data_point, name = 'add_data_point'),
    path('add-data-point/', views.add_data_point, name = 'add_data_point'),
    path('reset-data-point/', views.reset_data_points, name = 'reset_data_points'),
    path('route/<str:origin>/<str:destination>/', views.route, name = 'route'),
    path('route/', views.route, name = 'route'),
    path('list-data-points/<str:origin>/<str:destination>/<str:type>/', views.list_data_points, name = 'list_data_points'),
    path('process-sns-message/', views.process_sns_message, name = 'process_sns_message'),
    path('add-user/', views.add_user, name = 'add_user'),
    path('login/', views.user_login, name = 'user_login'),
    path('', views.home, name = 'home'),
]

