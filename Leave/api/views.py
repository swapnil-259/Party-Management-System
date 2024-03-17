from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from Party.models import User,PartyStatus,PartyRequest,AfterPartyStatus,RequestedMembers
from StudentDetails.models import Student_primdetail,TeamERP
from datetime import datetime
from Leave.models import LeaveRequest,LeaveStatus
from Leave.api.serializers import LeavePostSerializer,LeaveGetSerializer,LeaveStatusPutSerializer,LeaveStatusGetSerializer,StatusDashboardSerializer,AcceptedDashboardSerializer,PreviousLeaveSerializer
from StudentDetails.api.authentication import CsrfExemptSessionAuthentication
from Party.api.serializers import PartyDetailsSerializer,AfterPartyNotificationSerializer
from Reimbursement.api.serializers import RStatusSerializer
from Reimbursement.models import ReimbursementStatus
from django.core.mail import send_mail
from django.template.loader import render_to_string
from Backend import settings



        
class AddLeaveAV(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
      
    def post(self, request):
            user_id = self.request.user.id
            user=Student_primdetail.objects.get(Lib_id__username=self.request.user)
            Lserializer = LeavePostSerializer(data=request.data)
            if User.objects.filter(id=user_id,counter__lte=0).exists():
                if Lserializer.is_valid():
                    from_date=Lserializer.validated_data['from_date']
                    to_date=Lserializer.validated_data['to_date']
                    if to_date<from_date:
                        return Response({'message':'To date cannot be before from date'},status=status.HTTP_400_BAD_REQUEST)
                    leave=Lserializer.save(asked_by_id=user.Uniq_Id)
                    
                    leaveid=LeaveRequest.objects.get(id=leave.id)
                    
                    user_y=User.objects.get(id=user_id)
                    uyear=user_y.year
                    
                    if (uyear==1 or uyear==2 or uyear==3):
                        to_users=Student_primdetail.objects.filter(Lib_id__year__gt=uyear).values_list('Uniq_Id',flat=True).first()
                    
                       
                        
                    elif uyear==4:
                        to_users=Student_primdetail.objects.filter(Lib_id__year=uyear).exclude(Lib_id=user_id).values_list('Uniq_Id',flat=True).first()   
                    leavestatus=LeaveStatus.objects.create(
                            leave=leaveid,
                           
                        )
                            
                    
                    return Response({"message":"Requested successfully"},status=status.HTTP_200_OK)
                                
                    
                else:
                    return Response(Lserializer.errors)       
            else:
                return Response({"message":"Clear Pending Parties"},status=status.HTTP_400_BAD_REQUEST)
                    
                    
    def get(self,request):
        
        new = LeaveRequest.objects.all()
        serializer = LeaveGetSerializer(new, many=True)
        return Response(serializer.data)
            
            
    
class LeaveStatusAV(APIView):  
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
      
    def put(self, request, pk):
        query = LeaveStatus.objects.get(pk=pk)
        serializer = LeaveStatusPutSerializer(query, data=request.data)
        user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user)
        if serializer.is_valid():
            data=serializer.save(response_by_id=user_id.Uniq_Id)
            leaveid=LeaveStatus.objects.get(id=pk)
            leave_id=leaveid.leave
            if serializer.data['status']==1:
                LeaveRequest.objects.filter(id=leave_id.id).update(final_status=1)
            else:
                LeaveRequest.objects.filter(id=leave_id.id).update(final_status=0)
            
            leave=LeaveRequest.objects.get(id=leave_id.id)
            emailuser=Student_primdetail.objects.get(Uniq_Id=leave.asked_by.Uniq_Id)
        
            
            if serializer.data['status']==1:
                context = {
                                'reason': leave.reason,
                                'from_date': leave.from_date,
                                'to_date': leave.to_date,
                          }
                                    
                email_content = render_to_string('Leave/leave.html', context)
                sender=settings.DEFAULT_FROM_EMAIL
                subject = 'Leave Approval'
                from_email = sender
                recipient_list = [emailuser.Email_id]
                send_mail(subject, 'Leave Approval', from_email, recipient_list,
                        html_message=email_content)
                    
            return Response({"message":"leave status updated"},status=status.HTTP_200_OK)
    
        else:

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            
    
class AcceptedLeavesAV(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user)
    
        new = LeaveRequest.objects.filter(asked_by_id=user_id.Uniq_Id,final_status=1).all()
        serializer = AcceptedDashboardSerializer(new,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    
class RejectedLeavesAV(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user)
        new = LeaveRequest.objects.filter(asked_by_id=user_id.Uniq_Id,final_status=0).all()
        serializer = AcceptedDashboardSerializer(new,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class PendingLeavesAV(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user)
        new = LeaveRequest.objects.filter(asked_by_id=user_id.Uniq_Id,final_status__isnull=True).all()
        serializer = AcceptedDashboardSerializer(new,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
class ALLNotificationsAV(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        
        
        user=User.objects.get(id=self.request.user.id)
        user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user)
        juniors=list(TeamERP.objects.filter(uniq_id__Lib_id__year__lt=user.year).values_list('uniq_id',flat=True))
        data=[]
        for i in juniors:
            if LeaveStatus.objects.filter(leave__asked_by=i,leave__final_status__isnull=True).exists():
                queryset=LeaveStatus.objects.filter(leave__asked_by=i,leave__final_status__isnull=True)
                data.extend(queryset)
        if user.year==4:
            teammates=list(TeamERP.objects.filter(uniq_id__Lib_id__year=user.year).exclude(uniq_id__Lib_id__username=self.request.user).values_list('uniq_id',flat=True))
            for i in teammates:
              if LeaveStatus.objects.filter(leave__asked_by=i,leave__final_status__isnull=True).exists():
                queryset=LeaveStatus.objects.filter(leave__asked_by=i,leave__final_status__isnull=True)
                data.extend(queryset)
                
                
        leave_serializer = LeaveStatusGetSerializer(data,many=True)
        
        party = PartyStatus.objects.filter(response_by_id=user_id.Uniq_Id,status=0)
        party_serializer = PartyDetailsSerializer(party,many=True)
        
        reim = ReimbursementStatus.objects.filter(requested_to=user_id.Uniq_Id,status=0)
        reim_serializer = RStatusSerializer(reim,many=True)
        
        after_party = AfterPartyStatus.objects.filter(response_by=user_id.Uniq_Id,status=0)
        after_serializer = AfterPartyNotificationSerializer(after_party,many=True)
        
        serializer=leave_serializer.data+party_serializer.data+reim_serializer.data +after_serializer.data
        return Response(serializer)
    
        
    
class DataGraphAV(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user)
        data=[]
        P_given=data.append({"type":"Given Parties","value":RequestedMembers.objects.filter(giver_id=user_id.Uniq_Id).filter(party__grant=1).count()})
        P_counter=User.objects.filter(id=user_id.Lib_id.id).first()
        if P_counter.counter<0:
            p_pending=data.append({"type":"Party bonus","value":abs(P_counter.counter)})
        else:
            p_pending=data.append({"type":"Pending parties","value":P_counter.counter})
        L_accepted = data.append({"type":"Accepted leaves","value":LeaveRequest.objects.filter(asked_by_id=user_id.Uniq_Id,final_status=1).count()})
        L_rejected = data.append({"type":"Rejected leaves","value":LeaveRequest.objects.filter(asked_by_id=user_id.Uniq_Id,final_status=0).count()})
        L_pending = data.append({"type":"Pending leaves","value":LeaveRequest.objects.filter(asked_by_id=user_id.Uniq_Id,final_status__isnull=True).count()})

        
        return Response(data,status=status.HTTP_200_OK)
    
        
class PreviousAV(generics.ListAPIView):
    def get(self, request):
        user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user) 
        queryset = LeaveRequest.objects.filter(asked_by=user_id.Uniq_Id).order_by('-asked_on')
        serializer = PreviousLeaveSerializer(queryset, many=True)
        return Response(serializer.data)
        
      
    
    
    
        
      
    
    
    