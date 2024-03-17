from django.urls import path
from Backend import settings
# from django.conf.urls.static import static

from StudentDetails.api.views import ChangePassword, Logout, Login, NewPassword, OtpGeneration, OtpValidation, UserDetails, Users

urlpatterns = [
   # path('register/',Register.as_view(),name='register'),
   path('login/',Login.as_view(),name='login'),
   path('logout/',Logout.as_view(),name='logout'),
   path('profile/',UserDetails.as_view(),name='user_details'),
   path('dropdown/',Users.as_view(),name='dropdown'),
   path('change_password/',ChangePassword.as_view(),name='change-password'),
   path('otp_generation/',OtpGeneration.as_view(),name='otp-generation'),
   path('otp_validation/',OtpValidation.as_view(),name='otp-validation'),
   path('forgot_password/',NewPassword.as_view(),name='forgot-password'),



   

]