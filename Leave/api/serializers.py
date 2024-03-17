from rest_framework import serializers
from Leave.models import LeaveRequest,LeaveStatus

class LeavePostSerializer(serializers.ModelSerializer):
        
    class Meta:
        model=LeaveRequest
        fields=['from_date','to_date','reason']
        
        
class LeaveGetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=LeaveRequest
        exclude=['asked_by']
        
        
        
class LeaveStatusPutSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=LeaveStatus
        fields=['status']
        
        
class NameSerializer(serializers.ModelSerializer):
    class Meta:
        model=LeaveRequest
        fields=['asked_by']
    
 
class LeaveStatusGetSerializer(serializers.ModelSerializer):
    from_date=serializers.ReadOnlyField(source='leave.from_date')
    to_date=serializers.ReadOnlyField(source='leave.to_date')
    reason=serializers.ReadOnlyField(source='leave.reason')
    asked_on=serializers.ReadOnlyField(source='leave.asked_on')
    type = serializers.ReadOnlyField(default='Leave Request')
    asked_by=serializers.StringRelatedField(source='leave.asked_by.Name')
    class Meta:
        model=LeaveStatus
        fields=['from_date','to_date','reason','asked_on','asked_by','id','type']
    # def to_representation(self, instance):
    #     data=super().to_representation(instance) 
    #     return data  
        
class StatusDashboardSerializer(serializers.ModelSerializer):
    from_date=serializers.ReadOnlyField(source='leave.from_date')
    to_date=serializers.ReadOnlyField(source='leave.to_date')
    reason=serializers.ReadOnlyField(source='leave.reason')
    asked_by=serializers.StringRelatedField(source='leave.asked_by.Name')
    class Meta:
        model=LeaveStatus
        fields=['from_date','to_date','reason','asked_by']
        
        
class AcceptedDashboardSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=LeaveRequest
        fields=['from_date','to_date','reason']
        
        
    
class PreviousLeaveSerializer(serializers.ModelSerializer):
    asked_on = serializers.DateTimeField(read_only=True,format="%d-%m-%Y(%H:%M)")
    class Meta:
        model=LeaveRequest
        exclude=['asked_by']
        
    def to_representation(self, instance):
        
        data= super().to_representation(instance)
        status=data['final_status']
        if status==None:
            status='Pending'
        elif status==1:
            status='Accepted'
        else:
            status='Rejected'
        data['final_status']=status
        
        return data
        
        

        

    