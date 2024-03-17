from datetime import datetime
from rest_framework import status
from rest_framework import generics
from Party.api.serializers import (AfterPartyNotificationSerializer, AfterPartySerializer, AfterPartyStatusSerializer,
                                    GivePartyHistorySerializer, GivePartySerializer, GraphSerializer, PartyAcceptedUserData,
                                      PartyApprovalSerializer, PartyDetailsSerializer, PartyDropdownSerializer, 
                                      PartyHistorySerializer, PartyImageSerializer, PartyImagesSerializer,
                                        PartyNameSerializer, PartyPendingUserData, PartyRejectedUserData, PartySerializer,MembersSerializer,
                                          PartyStatusSerializer,PartyUserData)
from rest_framework.views import APIView
from rest_framework.response import Response
from Party.models import AfterPartyStatus, GivePartyRequest, PartyImages, PartyRequest, RequestedMembers,PartyStatus
from StudentDetails.models import Student_primdetail, TeamERP,User
from Leave.models import LeaveRequest
from django.core.mail import send_mail
from Backend import settings
from StudentDetails.api.authentication import IsAuthenticated
from StudentDetails.api.authentication import CsrfExemptSessionAuthentication
from django.template.loader import render_to_string
from datetime import datetime




class Party(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes=[IsAuthenticated]
    def post(self,request):
        if request.data.get('users') is None:
            return Response({'message':'users field is required'},status=status.HTTP_400_BAD_REQUEST)
        users=request.data['users']
        if not users:
            return Response({'message':'party requested to None'},status=status.HTTP_400_BAD_REQUEST)
        serializer=PartySerializer(data=request.data)
        if serializer.is_valid():
            user=Student_primdetail.objects.get(Lib_id__username=self.request.user)
            id=serializer.save(initiated_by_id=user.Uniq_Id)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        date=datetime.now().date()
        leave=list(LeaveRequest.objects.filter(from_date__lte=date,to_date__gte=date,final_status=True).values_list('asked_by',flat=True)) 
        total_members=list(TeamERP.objects.all().exclude(uniq_id__Lib_id__username=self.request.user).values_list('uniq_id',flat=True))
        result1=[]
        for i in total_members:
            if i not in leave:
                result1.append(i)
        results=set(result1)^set(users)
        for user in users:
           member_serializer=MembersSerializer(data={'party':id.id,'giver':user})
           if member_serializer.is_valid():
                member_serializer.save()
           else:
                return Response(member_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        for result in results:  
              status_serializer=PartyStatusSerializer(data={'party':id.id,'response_by':result})
              if status_serializer.is_valid():
                  status_serializer.save()
              else:
                  return Response(status_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response({'message':'Party Requested'},status=status.HTTP_201_CREATED)



class Partydetails(generics.ListAPIView):
    serializer_class=PartyDetailsSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        user=Student_primdetail.objects.get(Lib_id__username=self.request.user)
        return PartyStatus.objects.filter(response_by_id=user.Uniq_Id,status=0)

class PartyApproval(APIView):
   authentication_classes=(CsrfExemptSessionAuthentication,)
   permission_classes=[IsAuthenticated]
   def put(self,request,pk):
       data={}
       data['status']=1
       serializer=PartyApprovalSerializer(data=data)
       if serializer.is_valid():
           user=Student_primdetail.objects.get(Lib_id__username=self.request.user)
           PartyStatus.objects.filter(party=pk,response_by_id=user.Uniq_Id).update(status=1)
           members=PartyStatus.objects.filter(party=pk).count()
           approve_status=PartyStatus.objects.filter(party=pk,status=1).count()
           if members==approve_status:
                receipients=list(RequestedMembers.objects.filter(party=pk).values_list('giver',flat=True))
                party=PartyRequest.objects.get(id=pk)
                to_list=[]
                data={
                    "PartyReason":party.reason,
                    "ReasonDate":party.date
                }
                sender=settings.DEFAULT_FROM_EMAIL
                for i in receipients:
                    email=Student_primdetail.objects.select_related('Lib_id').get(Lib_id=i)
                    user=email.Lib_id
                    user.counter+=1
                    user.save()
                    to_list.append(email.Email_id)
                send_mail(subject="Regarding Party",message="Party has been accepted",from_email=sender,recipient_list=to_list,html_message=render_to_string('Party/email.html',context=data))  
                party.status=1
                party.save()      
           return Response({'message':'Party Accepted'},status=status.HTTP_200_OK)
       else:
           return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
       
class PartyDropdown(generics.ListAPIView):

    permission_classes=[IsAuthenticated]
    serializer_class= PartyDropdownSerializer

    def get_queryset(self):
        user=Student_primdetail.objects.get(Lib_id__username=self.request.user)
        querys=list(PartyRequest.objects.filter(status=1,grant=0).values_list('id',flat=True))
        data=[]
        for i in querys:
            if not GivePartyRequest.objects.filter(party=i,status=0).exists():
                if RequestedMembers.objects.filter(party=i,giver=user.Uniq_Id):
                 queryset=PartyRequest.objects.filter(id=i)
                 data.extend(queryset)
    
        return data

    

class PartyReject(APIView):
   authentication_classes=(CsrfExemptSessionAuthentication,)
   permission_classes=[IsAuthenticated]

   def put(self,request,pk):
       data={}
       data['status']=2
       serializer=PartyApprovalSerializer(data=data)
       if serializer.is_valid():
           user=Student_primdetail.objects.get(Lib_id__username=self.request.user)
           PartyStatus.objects.filter(party=pk,response_by_id=user.Uniq_Id).update(status=2)
           members=PartyStatus.objects.filter(party=pk).count()
           approve_status=PartyStatus.objects.filter(party=pk,status=1).count()
           reject_status=PartyStatus.objects.filter(party=pk,status=2).count()
         
           if members==approve_status+reject_status:
             receipients=list(RequestedMembers.objects.filter(party=pk).values_list('giver',flat=True))
             party=PartyRequest.objects.get(id=pk)
             to_list=[]
             data={
                    "PartyReason":party.reason,
                    "ReasonDate":party.date
                } 
             for i in receipients:
                    email=Student_primdetail.objects.get(Lib_id=i)
                    to_list.append(email.Email_id)
             sender=settings.DEFAULT_FROM_EMAIL
             send_mail(subject="Regarding Party",message="Party has been rejected",from_email=sender,recipient_list=to_list,html_message=render_to_string('Party/email.html',context=data))
             party.status=2
             party.save()  
           return Response({'message':'Party Rejected'},status=status.HTTP_200_OK)
       else:
           return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class Give(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=(CsrfExemptSessionAuthentication,)

    def post(self,request):
        if request.data.getlist('image') is None:
            return Response({'message':'Images are required'},status=status.HTTP_400_BAD_REQUEST)
        if request.data.getlist('money_spent') is None:
            return Response({'message':'Images are required'},status=status.HTTP_400_BAD_REQUEST)
        pk=request.data['party']
        image=request.FILES.getlist('image')
        if not image:
            return Response({'message':'image required'},status=status.HTTP_400_BAD_REQUEST)
        give_serializer=GivePartySerializer(data=request.data)
        if give_serializer.is_valid():
            give=give_serializer.save()
        else:
            return Response(give_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        for  i in image:
            serializer=PartyImageSerializer(data={'image':i,'party':give.id})
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        members=list(PartyStatus.objects.filter(party=pk).values_list('response_by',flat=True))
        initiated_by=list(PartyRequest.objects.filter(id=pk).values_list('initiated_by',flat=True))
        for i in members:
            party_serializer=AfterPartySerializer(data={'party_id':give.id,'response_by':i})
            if party_serializer.is_valid():
                party_serializer.save()
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        for i in initiated_by:
            party_serializer=AfterPartySerializer(data={'party_id':give.id,'response_by':i})
            if party_serializer.is_valid():
                party_serializer.save()
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        return Response({'message':'Uploaded Successfully'})
    

class AfterPartyApproval(APIView):
   permission_classes=[IsAuthenticated]
   authentication_classes=(CsrfExemptSessionAuthentication,)

   def put(self,request,pk):
       serializer=AfterPartyStatusSerializer(data=request.data)
       party=AfterPartyStatus.objects.select_related('party_id').get(id=pk)
       give=party.party_id
       id=give.party
       count=AfterPartyStatus.objects.filter(party_id=pk).count()
       if serializer.is_valid():
           user=Student_primdetail.objects.get(Lib_id__username=self.request.user)
           AfterPartyStatus.objects.filter(id=pk,response_by=user.Uniq_Id).update(status=serializer.data['status'])
           accepted=AfterPartyStatus.objects.filter(party_id=give,status=1).count()
           rejected=AfterPartyStatus.objects.filter(party_id=give,status=2).count()
           if count==accepted:
               members=list(RequestedMembers.objects.filter(party=id).values_list('giver',flat=True))
               member_count=len(members)
               for member in members:
                   counter=Student_primdetail.objects.select_related('Lib_id').get(Lib_id=member)
                   money="{:.2f}".format(counter.Lib_id.contribution+give.money_spent/member_count)
                   user_id=Student_primdetail.objects.get(Uniq_Id=member)
                   User.objects.filter(id=user_id.Lib_id.id).update(contribution=money,counter=counter.Lib_id.counter-1)
               PartyRequest.objects.filter(id=id.id).update(grant=True,money_spent=give.money_spent)
               GivePartyRequest.objects.filter(id=give.id).update(status=1)
               return Response({'message':'Approve Successfull'},status=status.HTTP_200_OK)
           elif count==accepted+rejected:
               GivePartyRequest.objects.filter(id=give.id).update(status=2)  
               return Response({'message':'Denied Successfull'},status=status.HTTP_200_OK)
           return Response({'message':'Response Recorded'})
       else:
           return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
       


class AfterPartyDetails(generics.ListAPIView):

    permission_classes=[IsAuthenticated]
    serializer_class=AfterPartyNotificationSerializer

    def get_queryset(self):
        user=Student_primdetail.objects.get(Lib_id__username=self.request.user)
        return AfterPartyStatus.objects.filter(response_by_id=user.Uniq_Id,status=0)


class PartyAccepted(generics.ListAPIView):
    serializer_class=PartyUserData
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return PartyRequest.objects.filter(status=1)
    
class PartyPending(generics.ListAPIView):
    serializer_class=PartyUserData
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return PartyRequest.objects.filter(status=0)
    
class PartyRejected(generics.ListAPIView):
    serializer_class=PartyUserData
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return PartyRequest.objects.filter(status=2)
    
    
class UpcomingParties(generics.ListAPIView):
        
        serializer_class=PartyUserData
        permission_classes=[IsAuthenticated]
         
        def get_queryset(self):
            return  PartyRequest.objects.filter(status=1,grant=False).order_by('created_time')
    
           
           
class Graph(generics.ListAPIView):

    permission_classes=[IsAuthenticated]
    serializer_class=GraphSerializer

    def get_queryset(self):
        return Student_primdetail.objects.all()

        

class AfterPartyImage(generics.ListAPIView):

    permission_classes=[IsAuthenticated]
    serializer_class=PartyImagesSerializer

    def get_queryset(self):
        pk=self.kwargs.get('pk')
        if pk is None:
            return Response({'message':'Party data not provided'},status=status.HTTP_400_BAD_REQUEST)
        return PartyImages.objects.filter(party=pk,status=True)
    


class PartyHistory(generics.ListAPIView):

    serializer_class=PartyHistorySerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        user=Student_primdetail.objects.get(Lib_id__username=self.request.user)
        return PartyRequest.objects.filter(initiated_by=user.Uniq_Id)


class GivePartyHistory(generics.ListAPIView):

    permission_classes=[IsAuthenticated]
    serializer_class=GivePartyHistorySerializer
 
    def get_queryset(self):
        data=[]
        party_id=list(GivePartyRequest.objects.all().distinct().values_list('party',flat=True))
        for id in party_id:
            user=Student_primdetail.objects.get(Lib_id__username=self.request.user)
            if RequestedMembers.objects.filter(party=id,giver=user.Uniq_Id):
                queryset=GivePartyRequest.objects.filter(party=id)
                data.extend(queryset)
        return data
    
class PartyPendings(generics.ListAPIView):
    
    permission_classes=[IsAuthenticated]

    def get(self,request):
        user=Student_primdetail.objects.get(Lib_id__username=self.request.user)
        data1=[]
        data2=[]
        data3=[]
        data4=[]
        pending= list(PartyRequest.objects.filter(status=0))
        for i in pending:
            if PartyStatus.objects.filter(party=i,response_by=user.Uniq_Id,status=1).exists():
                queryset=PartyRequest.objects.filter(id=i.id)
                data1.extend(queryset)
            elif PartyStatus.objects.filter(party=i,response_by=user.Uniq_Id,status=2).exists():
                queryset=PartyRequest.objects.filter(id=i.id)
                data3.extend(queryset)    
            elif PartyStatus.objects.filter(party=i,response_by=user.Uniq_Id,status=0).exists():
                queryset=PartyRequest.objects.filter(id=i.id)
                data4.extend(queryset)        
            else:
               queryset=PartyRequest.objects.filter(id=i.id)
               data2.extend(queryset)
        accepted_serializer=PartyAcceptedUserData(data1,many=True)
        pending_serializer=PartyPendingUserData(data4,many=True)
        rejected_serializer=PartyRejectedUserData(data3,many=True)
        normal_serializer=PartyUserData(data2,many=True)
        serializer=accepted_serializer.data+pending_serializer.data+rejected_serializer.data+normal_serializer.data
        return Response(serializer)



