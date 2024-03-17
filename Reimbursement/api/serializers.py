from rest_framework import serializers
from rest_framework.validators import ValidationError
from Reimbursement.models import ReimbursementRequest,ReimbursementStatus
from Party.models import PartyRequest,RequestedMembers



class ReimbursementSerializer(serializers.ModelSerializer):
        
    class Meta:
        model=ReimbursementRequest
        fields=['party','reason']
        
class RequestGetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=ReimbursementRequest
        fields='__all__'
        
class RStatusSerializer(serializers.ModelSerializer):
    party=serializers.ReadOnlyField(source='reimbursement.party.reason')
    requestor=serializers.ReadOnlyField(source='reimbursement.requestor.Name')
    type = serializers.ReadOnlyField(default='Reimbursement')
    class Meta:
        model=ReimbursementStatus
        fields=['status','party','requestor','type','reimbursement']
        
        
        
class InnerPartySerializer(serializers.ModelSerializer):
    class Meta:
        model=PartyRequest
        fields=['reason','date']
       
class InnerRSerializer(serializers.ModelSerializer):
    requestor=serializers.ReadOnlyField(source='requestor.Name')
    class Meta:
        model=ReimbursementRequest
        fields=['requestor']
        
        
class RStatusGetSerializer(serializers.ModelSerializer):
    reimbursement=InnerRSerializer(many=True,read_only=True,allow_null=True)
    class Meta:
        model=ReimbursementStatus
        fields=['reimbursement','status']
        
        
class CompletedPartySerializer(serializers.ModelSerializer):
        
        party=serializers.ReadOnlyField(source='party.reason')

        
        class Meta:
            model=RequestedMembers
            fields=['party','party_id']
            
            
class ReimbursementNotifSerializer(serializers.ModelSerializer):
        
    class Meta:
        model=ReimbursementStatus
        fields=['status']
        
class RPopupStatusSerializer(serializers.ModelSerializer):
    party=serializers.ReadOnlyField(source='party.reason')
    class Meta:
        model=ReimbursementRequest
        fields=['status','party','status_time','reason']
        
    def to_representation(self, instance):
        data= super().to_representation(instance)
        data['status_time']=instance.status_time.date()
       
        return data
        
        
class PreviousReSerializer(serializers.ModelSerializer):
    status_time = serializers.DateTimeField(read_only=True,format="%Y-%m-%d")
    party = serializers.ReadOnlyField(source='party.reason')
    class Meta:
        model=ReimbursementRequest
        exclude=['requestor']
        
    def to_representation(self, instance):
        
        data= super().to_representation(instance)
        status=data['status']
        if status==None:
            status='Pending'
        elif status==1:
            status='Accepted'
        else:
            status='Rejected'
        data['status']=status
        
        return data
        
        
        