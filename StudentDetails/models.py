from django.db import models
from Party.models import User

class Student_primdetail(models.Model):
    Name = models.CharField(max_length=500,null=False)
    Batch_from = models.IntegerField(null=False)
    Batch_to = models.IntegerField(null=False)
    Uni_Roll_No = models.CharField(max_length=15,null=True)
    Join_Year = models.IntegerField(null=False)
    Email_id  = models.CharField(max_length=500,null=False)
    Date_of_Birth = models.DateField(null=False)
    Uniq_Id = models.BigIntegerField(primary_key=True,unique=True)
    Lib_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='Library')
    time_stamp = models.DateTimeField(auto_now_add=True)
    Kiet_Email_id = models.CharField(max_length=500,null=True)
    Fee_Waiver = models.BooleanField(default=False)
    class Meta :
        db_table = "Student_primdetail"

class TeamRole(models.Model):
    role = models.CharField(max_length=50, null=False)
    priority = models.IntegerField(null=False)
    
    class Meta:
        db_table = "TeamRole"


class TeamERP(models.Model):
    uniq_id = models.ForeignKey("StudentDetails.Student_primdetail",null=True,on_delete=models.SET_NULL,related_name='prim_details')
    image = models.ImageField(null=True)
    linked_in = models.CharField(max_length=500,null=True)
    github = models.CharField(max_length=500,null=True)
    role = models.ForeignKey(TeamRole,null=True,on_delete=models.SET_NULL,related_name='erp_role')
    status = models.CharField(max_length=10,null=True)
    
    class Meta:
        db_table = "TeamERP"
    

# class TeamERPCounter(models.Model):
#     erp=models.ForeignKey(TeamERP,on_delete=models.SET_NULL,null=True,related_name='erp_member')
    

    
