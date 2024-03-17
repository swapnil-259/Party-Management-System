from rest_framework import serializers
from Party.models import (GivePartyRequest, PartyImages, RequestedMembers,
                          PartyRequest,PartyStatus,AfterPartyStatus)
from StudentDetails.models import Student_primdetail, User

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model=PartyRequest
        fields=['date','reason']


class MembersSerializer(serializers.ModelSerializer):

    class Meta:
        model=RequestedMembers
        fields='__all__'


class PartyStatusSerializer(serializers.ModelSerializer):
    party_status=PartySerializer(read_only=True,many=True)
    class Meta:
        model=PartyStatus
        fields='__all__'

class PartyApprovalSerializer(serializers.ModelSerializer):

    class Meta:
        model=PartyStatus
        fields=['status'] 

class PartyImageSerializer(serializers.ModelSerializer):

    class Meta:
        model=PartyImages
        fields='__all__'    



class AfterPartySerializer(serializers.ModelSerializer):

    class Meta:
        model=AfterPartyStatus
        fields='__all__'


class AfterPartyStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model=AfterPartyStatus
        fields=['status']




class PartyNameSerializer(serializers.ModelSerializer):

    class Meta:
        model=PartyRequest
        fields=['reason','date','id']


class GivePartySerializer(serializers.ModelSerializer):  
     
   
     class Meta:
        model=GivePartyRequest
        fields=['party','money_spent']


class GivePartyHistorySerializer(serializers.ModelSerializer):

     party=PartyNameSerializer(read_only=True)
     
     class Meta:
        model=GivePartyRequest
        fields=['party','money_spent','status']
     def to_representation(self, instance):
         data=super().to_representation(instance)
         data['reason']=instance.party.reason
         data['date']=instance.party.date
         status=instance.status
         if status==1:
            data['status']="Approved"
         elif status==2:
            data['status']="Rejected"
         else:
            data['status']="Pending"
         data.pop('party')
         return data
    
class PartyDetailsSerializer(serializers.ModelSerializer):

    party=PartyNameSerializer(read_only=True)
    initiated_by=serializers.ReadOnlyField(source='party.initiated_by.Name')

    class Meta:
        model=PartyStatus
        fields=['party','initiated_by']

    def to_representation(self, instance):
       data= super().to_representation(instance)
       data['id']=instance.party.id
       data['party']=instance.party.reason
       data['date']=instance.party.date
       data['type']="Party Request "
       return data


class RequestedMembersSerializer(serializers.ModelSerializer):

    class Meta:
        model=Student_primdetail
        fields=['Name']


class PartyGiver(serializers.ModelSerializer):

    giver=serializers.ReadOnlyField(source='giver.Name')
    

    class Meta:
        model=RequestedMembers
        fields=['giver']


class PartyUserData(serializers.ModelSerializer):
      
      party_requested_to=PartyGiver(many=True)
      initiated_by=RequestedMembersSerializer()
      class Meta:
        model=PartyRequest
        fields=['reason','date','party_requested_to','initiated_by']


class PartyHistorySerializer(serializers.ModelSerializer):
      
      party_requested_to=PartyGiver(many=True)
      initiated_by=serializers.ReadOnlyField(source='initiated_by.Name')
      class Meta:
        model=PartyRequest
        fields=['reason','date','party_requested_to','initiated_by','status']

      def to_representation(self, instance):
          data=super().to_representation(instance)
          status=instance.status
          if status==1:
              data['status']="Approved"
          elif status==2:
              data['status']="Rejected"
          else:
              data['status']="Pending"
          return data



class UpcomingBirthdaysSerializer(serializers.ModelSerializer):

     class Meta:
        model=Student_primdetail
        fields=['Name','Date_of_Birth']

class PartyDropdownSerializer(serializers.ModelSerializer):

     class Meta:
        model=PartyRequest
        fields=['reason','id']



class GraphSerializer(serializers.ModelSerializer):
    Lib_id=serializers.ReadOnlyField(source='Lib_id.contribution')
    class Meta:
        model=Student_primdetail
        fields=['Name','Lib_id']

    def to_representation(self, instance):
        data=super().to_representation(instance)
        contribution=instance.Lib_id
        data['contribution']=instance.Lib_id.contribution
        data.pop('Lib_id')
        return data

class GivePartyDetailsSerializer(serializers.ModelSerializer):  
     
     party_give=PartyNameSerializer(read_only=True)
     
     class Meta:
        model=GivePartyRequest
        fields=['party','money_spent','id','party_give']

class AfterPartyNotificationSerializer(serializers.ModelSerializer):

    party_id=GivePartyDetailsSerializer()

    class Meta:
        model=AfterPartyStatus
        fields=['party_id','id']
    
    def to_representation(self, instance):
        data= super().to_representation(instance)
        data['party_id']=instance.party_id.id
        data['reason']=instance.party_id.party.reason
        data['date']=instance.party_id.party.date
        # data['money spent']=instance.party_id.money_spent
        data['type']="Party Review"
        return data

class PartyImagesSerializer(serializers.ModelSerializer):
    
    image_url = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model=PartyImages
        fields=['image_url']
    def get_image_url(self, obj):
        return obj.image.url
    
class PartyAcceptedUserData(serializers.ModelSerializer):
      
      party_requested_to=PartyGiver(many=True)
      initiated_by=RequestedMembersSerializer()
      user_status=serializers.ReadOnlyField(default="Approved")
      class Meta:
        model=PartyRequest
        fields=['reason','date','party_requested_to','initiated_by','user_status']


class PartyRejectedUserData(serializers.ModelSerializer):
      
      party_requested_to=PartyGiver(many=True)
      initiated_by=RequestedMembersSerializer()
      user_status=serializers.ReadOnlyField(default="Rejected")
      class Meta:
        model=PartyRequest
        fields=['reason','date','party_requested_to','initiated_by','user_status']

class PartyPendingUserData(serializers.ModelSerializer):
      
      party_requested_to=PartyGiver(many=True)
      initiated_by=RequestedMembersSerializer()
      user_status=serializers.ReadOnlyField(default="Pending")
      class Meta:
        model=PartyRequest
        fields=['id','reason','date','party_requested_to','initiated_by','user_status']
