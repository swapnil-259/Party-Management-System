from django.urls import path
from Leave.api.views import AddLeaveAV,LeaveStatusAV,ALLNotificationsAV,PendingLeavesAV,RejectedLeavesAV,AcceptedLeavesAV,DataGraphAV,PreviousAV

urlpatterns = [

   path('add_leave/', AddLeaveAV.as_view(), name='add-leave'),
   path('leave_status/<int:pk>', LeaveStatusAV.as_view(), name='leave-status'),
   path('notification/', ALLNotificationsAV.as_view(), name='leave-notification'),
   path('accepted/', AcceptedLeavesAV.as_view(), name='accepted-leaves'),
   path('pending/', PendingLeavesAV.as_view(), name='pending-leaves'),
   path('rejected/', RejectedLeavesAV.as_view(), name='rejected-leaves'),
   path('graph/', DataGraphAV.as_view(), name='all-approved-leaves'),
   path('previous/', PreviousAV.as_view(), name='all-previous-leaves'),
   
]