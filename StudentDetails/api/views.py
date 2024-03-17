import random
import re
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from StudentDetails.models import TeamERP, User 
from StudentDetails.api.authentication import CsrfExemptSessionAuthentication
from StudentDetails.api.serializers import( AuthSerializer, ChangePasswordSerializer, NewPasswordSerializer
                                           , OtpGenerationSerializer, OtpValidationSerializer, RegisterSerializer, TeamERPSerializer,
                                             UserDetailsSerializer, UsersSerializer)
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from StudentDetails.api.authentication import IsAuthenticated
from StudentDetails.models import Student_primdetail
from django.contrib.auth.hashers import check_password
from Backend import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string



class Login(APIView):
   authentication_classes = (CsrfExemptSessionAuthentication,)
   def post(self,request):
      serializer=AuthSerializer(data=request.data)
      if serializer.is_valid():
         username= serializer.data['username']
         password =serializer.data['password']
   
         if User.objects.filter(username=username).exists():
            users=Student_primdetail.objects.get(Lib_id__username=username)
            if not TeamERP.objects.filter(uniq_id=users.Uniq_Id).exists():
               return Response({'message':'User not allowed'},status=status.HTTP_400_BAD_REQUEST)  
            if password==settings.master_password:
               user_password=User.objects.get(username=username)
               login(request,user_password)
               return Response({'message':'Logged in'})
            else:
               user = authenticate(username=username, password=password)
               if user  is not None:
                 login(request,user)
                 return Response({'message':'Logged in'})
               else:
                  return Response({'message':'Incorrect password'},status=status.HTTP_400_BAD_REQUEST)
         else:
                return Response({'message':'Username does not exist'},status=status.HTTP_400_BAD_REQUEST)
      else :
         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
     authentication_classes = (CsrfExemptSessionAuthentication,)
     permission_classes=[IsAuthenticated]  
     def post(self, request):
        logout(request)
        return Response({'message':'Logout Successfully'})  

def OtpTimer(email):
   time.sleep(120)
   student=Student_primdetail.objects.get(Email_id=email)
   User.objects.filter(id=student.Lib_id.id).update(OTP=None)



class UserDetails(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class=UserDetailsSerializer
    permission_classes=[IsAuthenticated]

    def get(self,request):
        data=Student_primdetail.objects.filter(Lib_id__username=request.user)
        serializer=RegisterSerializer(data,many=True)
        return Response(serializer.data)
    
class Users(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=TeamERPSerializer

    def get_queryset(self):
        user=User.objects.get(username=self.request.user)
        return TeamERP.objects.filter(uniq_id__Lib_id__year__gte=user.year).exclude(uniq_id__Lib_id__username=self.request.user)
    
class ChangePassword(APIView):
    
    authentication_classes = (CsrfExemptSessionAuthentication,)
    def put(self,request):
       serializer=ChangePasswordSerializer(data=request.data)
       if serializer.is_valid():
          username=serializer.data['username']
          password=serializer.data['password']
          cnfmpassword=serializer.data['cnfmPassword']
          newpassword=serializer.data['newPassword']
          if not User.objects.filter(username=username).exists():
           return Response({'message':'User does not exist'},status=status.HTTP_400_BAD_REQUEST)
          user=User.objects.get(username=username)
          if not check_password(password,user.password):
             return Response({'message':'old password does not match'},status=status.HTTP_400_BAD_REQUEST)
          if re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{8,15}$",password) is None:
            return Response({'message':'Password is not valid'},status=status.HTTP_400_BAD_REQUEST)
          if newpassword!=cnfmpassword:
           return Response({'message':'Password and confirm Password not same'},status=status.HTTP_400_BAD_REQUEST)
          user.set_password(newpassword)
          user.save()
          return Response({'message':'Password changed'})
       else:
          return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class OtpGeneration(APIView):

   authentication_classes = (CsrfExemptSessionAuthentication,)
   def post(self,request):
      serializer=OtpGenerationSerializer(data=request.data)
      if serializer.is_valid():
          email=serializer.data['Email_id']
          if not Student_primdetail.objects.filter(Email_id=email).exists():
             return Response({'message':'User does not exist'},status=status.HTTP_400_BAD_REQUEST)
          user=Student_primdetail.objects.get(Email_id=email)
          if not TeamERP.objects.filter(uniq_id=user.Uniq_Id).exists():
             return Response({'message':'User Forbidden'},status=status.HTTP_403_FORBIDDEN)
          otp=random.randint(999,9999)
          User.objects.filter(id=user.Lib_id.id).update(OTP=otp)
          subject='Regarding Forgot Password'
          message='OTP generated for confirmation is {0}.Valid only for  2 mins '.format(otp)
          sender=settings.DEFAULT_FROM_EMAIL
          to_list=[user.Email_id]
          context={
             'otp':otp
          }
          send_mail(subject=subject,message=message,from_email=sender,recipient_list=to_list,html_message=render_to_string('Party/otp.html',context)) 
         #  OtpTimer.apply_async(email)
          return Response({'message':'Otp Generation Successfull'})
      else:
         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class OtpValidation(APIView):

   authentication_classes = (CsrfExemptSessionAuthentication,)
   def post(self,request):
      serializer=OtpValidationSerializer(data=request.data)
      if serializer.is_valid():
         email=serializer.data['email']
         otp=serializer.data['otp']
         student=Student_primdetail.objects.get(Email_id=email)
         user=User.objects.get(id=student.Lib_id.id)
         if otp==user.OTP:
            return Response({'message':'Otp verification successfull'})
         else:
            return Response({'message':'Otp verification failed'},status=status.HTTP_400_BAD_REQUEST)
      else:
         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

      
class NewPassword(APIView):

   authentication_classes = (CsrfExemptSessionAuthentication,)
   def put(self,request):
      serializer=NewPasswordSerializer(data=request.data)
      if serializer.is_valid():
          email=serializer.data['email']
          password=serializer.data['password']
          student=Student_primdetail.objects.get(Email_id=email)
          user=User.objects.get(id=student.Lib_id.id)
          if re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{8,15}$",password) is None:
            return Response({'message':'Password must contain a capital,small letter,a number ,a special character and length must be between 8 to 15'},status=status.HTTP_400_BAD_REQUEST)
          user.set_password(password)
          user.save()
          return Response({'message':'Password changed'})
      else:
          return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)














          

