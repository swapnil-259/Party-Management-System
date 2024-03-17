from django.db import models
from Party.models import BaseModel


class LeaveRequest(models.Model):
    asked_by  = models.ForeignKey("StudentDetails.Student_primdetail",on_delete=models.SET_NULL,null=True,related_name='lr_by_user')
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    asked_on = models.DateTimeField(auto_now_add=True)
    final_status = models.BooleanField(null=True)
    
class LeaveStatus(BaseModel):
    leave = models.ForeignKey(LeaveRequest,on_delete=models.SET_NULL,null=True,related_name='leave_request')
    response_by = models.ForeignKey("StudentDetails.Student_primdetail",on_delete=models.SET_NULL, null=True,related_name='lr_response_by')
