from django.db import models
from django.contrib.auth.models import AbstractUser


# from StudentDetails.models import Student_primdetail

class User(AbstractUser):
    counter=models.IntegerField(default=0)
    year=models.IntegerField(default=1)
    contribution=models.FloatField(default=0)
    OTP=models.CharField(max_length=10,null=True,blank=True)
    

class BaseModel(models.Model):
    status_choices=(
        (0,'pending'),
        (1,'accept'),
        (2,'reject')
    )
    status=models.IntegerField(status_choices,default=0)
    status_time=models.DateTimeField(auto_now=True)
    class Meta:
         abstract=True
        
class PartyRequest(BaseModel):
    initiated_by=models.ForeignKey("StudentDetails.Student_primdetail",on_delete=models.SET_NULL,null=True,related_name='party_initiated_by')
    date=models.DateField()
    reason=models.TextField()
    created_time=models.DateTimeField(auto_now_add=True)
    grant=models.BooleanField(default=False)
    money_spent=models.FloatField(default=0)
    

class RequestedMembers(models.Model):
    party=models.ForeignKey(PartyRequest,on_delete=models.SET_NULL,null=True,related_name='party_requested_to')
    giver=models.ForeignKey("StudentDetails.Student_primdetail",on_delete=models.SET_NULL,null=True,related_name='party_given_by')

class PartyStatus(BaseModel):
    party=models.ForeignKey(PartyRequest,on_delete=models.SET_NULL,null=True,related_name='party_status')
    response_by=models.ForeignKey("StudentDetails.Student_primdetail",on_delete=models.SET_NULL,null=True,related_name='pr_response_by')

class GivePartyRequest(BaseModel):
    party=models.ForeignKey(PartyRequest,on_delete=models.SET_NULL,null=True,related_name='party_give')
    money_spent=models.FloatField(default=0)

class PartyImages(models.Model):
    party=models.ForeignKey(GivePartyRequest,on_delete=models.SET_NULL,null=True,related_name='give_party_photos')
    image=models.FileField(upload_to='')
    status=models.BooleanField(default=True)

class AfterPartyStatus(BaseModel):
    party_id=models.ForeignKey(GivePartyRequest,on_delete=models.SET_NULL,null=True,related_name='give_party')
    response_by=models.ForeignKey("StudentDetails.Student_primdetail",on_delete=models.SET_NULL,null=True,related_name='party_members')
    


    
    
    
    
    
    
