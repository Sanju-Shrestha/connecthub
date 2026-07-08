from django.urls import path, include
from . import views 


 
app_name = "api" 
 
urlpatterns = [ 
    path(
    "users/", views.UserListAPIView.as_view(),
)
    


]