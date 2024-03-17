from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from StudentDetails.models import Student_primdetail
from Party.models import User
from datetime import datetime
from Reimbursement.models import ReimbursementRequest,ReimbursementStatus
from Reimbursement.api.serializers import ReimbursementSerializer,RStatusSerializer,RequestGetSerializer,RStatusGetSerializer,CompletedPartySerializer,ReimbursementNotifSerializer,RPopupStatusSerializer,PreviousReSerializer
from Party.models import PartyRequest,PartyStatus,RequestedMembers
from StudentDetails.api.authentication import CsrfExemptSessionAuthentication



class AddReimbursementAV(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self,request):
        
            new = ReimbursementRequest.objects.all()
            serializer = RequestGetSerializer(new, many=True)
            return Response(serializer.data)
      

    def post(self, request):
            user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user)
        
            serializer = ReimbursementSerializer(data=request.data)
            if serializer.is_valid():
                partyid=serializer.validated_data['party']
                
                if RequestedMembers.objects.filter(party_id=partyid.id,giver_id=user_id.Uniq_Id).exists():
                    if PartyRequest.objects.filter(id=partyid.id,status=1,grant=1).exists():
                   # if PartyRequest.objects.filter(id=partyid.id).exists():
                        if ReimbursementRequest.objects.filter(party=partyid,requestor=user_id).exists():
                            return Response({"message":"reimbursement request already raised for this particular party"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            serializer.save(requestor_id=user_id.Uniq_Id)
                                
                            participants =list( PartyStatus.objects.filter(party=partyid).values_list('response_by', flat=True))
                            r_request = ReimbursementRequest.objects.get(party=partyid,requestor=user_id)
                            initiated_by=PartyRequest.objects.filter(id=partyid.id).values_list('initiated_by',flat=True)
                            for participant_id in participants:
            
                                
                                request = ReimbursementStatus.objects.create(
                                    reimbursement=r_request,
                                    requested_to_id=participant_id
                                )
                            ReimbursementStatus.objects.create(
                                    reimbursement=r_request,
                                    requested_to_id=initiated_by
                                )
                            return Response({"message":"requested successfully"},status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Party Not granted"})
                else:
                    return Response({"message":"party not found"},status=status.HTTP_204_NO_CONTENT)
            else:
                    return Response(serializer.errors)
            

        
class RApprovalAV(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    def put(self, request, pk):
        user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user)
        query = ReimbursementStatus.objects.get(reimbursement_id=pk,requested_to_id=user_id.Uniq_Id)
        serializer = ReimbursementNotifSerializer(query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            c1=ReimbursementStatus.objects.filter(reimbursement_id=pk,status=1).count()
            c2=ReimbursementStatus.objects.filter(reimbursement_id=pk).count()
            c3=ReimbursementStatus.objects.filter(reimbursement_id=pk,status=2).count()
            if c1==c2:
                query=ReimbursementRequest.objects.filter(id=pk).all()
                query.update(status=1)
                requestor=ReimbursementRequest.objects.get(id=pk)
                student=Student_primdetail.objects.filter(Uniq_Id=requestor.requestor_id).first()

                counter=User.objects.get(id=student.Lib_id_id)
                counter.counter-=1
                counter.save()
            elif c2==c1+c3:
                query=ReimbursementRequest.objects.filter(id=pk).all()
                query.update(status=2)
                    
        
            return Response({"message":"status updated"},status=status.HTTP_200_OK)
    
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                
class ReNotificationAV(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request):
            
                new = ReimbursementRequest.objects.all()
                serializer = RStatusGetSerializer(new, many=True)
                return Response(serializer.data)
                

class CompletedPartiesAV(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user)
        if RequestedMembers.objects.filter(giver_id=user_id.Uniq_Id).exists():
            party_ids=list(RequestedMembers.objects.filter(giver_id=user_id.Uniq_Id).values_list('party_id',flat=True))
            if party_ids:
                data=[]
                for party_id in party_ids:
                    if ReimbursementRequest.objects.filter(party_id=party_id,requestor=user_id,status=1).exists():
                        pass
                    else:
                        data.append(party_id)
                query=RequestedMembers.objects.filter(giver_id=user_id.Uniq_Id,party_id__grant=1,party_id__in=data).all()   
                serializer = CompletedPartySerializer(query, many=True)
                return Response(serializer.data)
            else:
                return Response([])
        else:
            return Response([])
        
        
class RePopupAV(APIView):
    authentication_classes=(CsrfExemptSessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self,request):
        user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user)
        reim=ReimbursementRequest.objects.filter(requestor_id=user_id.Uniq_Id).all()
        reimserializer=RPopupStatusSerializer(reim,many=True)
        return Response(reimserializer.data,status=status.HTTP_200_OK)        
    
    
class RePreviousAV(generics.ListAPIView):
    def get(self, request):
        user_id = Student_primdetail.objects.get(Lib_id__username=self.request.user)
        queryset = ReimbursementRequest.objects.filter(requestor=user_id.Uniq_Id).order_by('status_time')
        serializer = PreviousReSerializer(queryset, many=True)
        return Response(serializer.data)   
    
    
                 
            
                
                
                
                
                
                

    



    
    
                 
            
                
                
                
                
                
                

    


