from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name="post_list"),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name="post_detail"),
    path('<int:post_id>/share/',views.post_share, name="post_share"),
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name="logout"),
    path('profile/', views.userAccount, name="profile"),
    path('editprofile/', views.updateProfile, name="editprofile"),
    path('edit_post/<int:post_id>',views.edit_post, name="edit_post"),
]