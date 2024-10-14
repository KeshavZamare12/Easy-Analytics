# users/urls.py
from django.urls import path
from .views import register, user_login,index,home,view_profile,edit_profile,\
user_logout,upload_file,modify_data_view,download_file,visualize_data,generate_plots,analyze_data_view,person_list

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path("",user_login, name="index"),
    path("home/",home, name="home"),
    path('profile/', view_profile, name='view_profile'),  # View profile page
    path('profile/edit/', edit_profile, name='edit_profile'),# Edit profile page
    path("logout/",user_logout, name="logout"),
    path("upload_data/",upload_file, name="upload_data"),
    path('modify/', modify_data_view, name='modify_data'),
    path('analyze/',analyze_data_view,name="analyze_data"),
    path('download/<int:id>', download_file, name='download_file'),
    path('visualize/', visualize_data, name='visualize_data'),
    path('generate-plots/', generate_plots, name='generate_plots'),
    path('table_data/',person_list, name="view_table"),
]

