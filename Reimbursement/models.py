from django.db import models
from django.db import models
from Party.models import User,PartyRequest,BaseModel




class ReimbursementRequest(BaseModel):
    
    requestor=models.ForeignKey("StudentDetails.Student_primdetail",models.SET_NULL,null=True,related_name="requestor_user")
    party=models.ForeignKey(PartyRequest,models.SET_NULL,null=True,related_name="ref_party")
    reason=models.CharField(max_length=200)

    
class ReimbursementStatus(BaseModel):
    reimbursement=models.ForeignKey(ReimbursementRequest,models.SET_NULL,null=True,related_name="ref_reimbursement")
    requested_to=models.ForeignKey("StudentDetails.Student_primdetail",models.SET_NULL,null=True,related_name="requested_to")
    
  
   
    
    
 
    
    
    