from django.urls import path
from Reimbursement.api.views import AddReimbursementAV,RApprovalAV,ReNotificationAV,CompletedPartiesAV,RePopupAV,RePreviousAV

urlpatterns = [

   path('add_reimbursement/', AddReimbursementAV.as_view(), name='add-reimbursement'),
   path('reimbursement_approval/<int:pk>', RApprovalAV.as_view(), name='reimbursement-approval'),
   path('notification/', ReNotificationAV.as_view(), name='leave-notification'),
   path('completed/', CompletedPartiesAV.as_view(), name='completed-parties'),
   path('popup/', RePopupAV.as_view(), name='reimbursement-status-popup '),
   path('previous/', RePreviousAV.as_view(), name='previous-reimbursements '),
   
]