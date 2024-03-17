
from rest_framework import serializers
from StudentDetails.models import  TeamERP, User

from StudentDetails.models import Student_primdetail



class AuthSerializer(serializers.Serializer):

     username= serializers.CharField()
     password = serializers.CharField(style={'input_type': 'password'})

class UsersSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Student_primdetail
        fields=['Name','Uniq_Id']

class TeamERPSerializer(serializers.ModelSerializer):

    uniq_id=UsersSerializer()
    class Meta:
        model=TeamERP
        fields=['uniq_id']

    def to_representation(self, instance):
        data= super().to_representation(instance)
        data['Name']=instance.uniq_id.Name
        data['Uniq_id']=instance.uniq_id.Uniq_Id
        data.pop('uniq_id')
        return data


class UserDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=User
        fields=['username']

class RegisterSerializer(serializers.ModelSerializer):

    Lib_id=UserDetailsSerializer()
    class Meta:
        model=Student_primdetail
        fields=['Name','Batch_from','Batch_to','Join_Year','Lib_id','Date_of_Birth','Email_id']
    
    def to_representation(self, instance):
        datas=super().to_representation(instance)
        datas['Lib_id']=instance.Lib_id.username
        results=(dict(datas))
        key=0
        ret=[]
        for result in results:
            values={}
            values['label']=list(results.keys())[key]
            values['key']=key
            values['children']=list(results.values())[key]
            key+=1
            ret.append(values)
        return ret
            
class ChangePasswordSerializer(serializers.Serializer):

     username= serializers.CharField()
     password = serializers.CharField(style={'input_type': 'password'})
     cnfmPassword=serializers.CharField(style={'input_type': 'password'})
     newPassword=serializers.CharField(style={'input_type': 'password'})

class OtpGenerationSerializer(serializers.ModelSerializer):

    class Meta:
        model=Student_primdetail
        fields=['Email_id']

class OtpValidationSerializer(serializers.Serializer):

    otp=serializers.CharField()
    email=serializers.CharField()

class NewPasswordSerializer(serializers.Serializer):
     email= serializers.CharField()
     password = serializers.CharField(style={'input_type': 'password'})
    #  cnfmPassword=serializers.CharField(style={'input_type': 'password'})