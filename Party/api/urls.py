from django.urls import path
from Backend import settings
from django.conf.urls.static import static

from Party.api.views import (AfterPartyApproval, AfterPartyDetails, AfterPartyImage,
                              Give, GivePartyHistory, Graph, Party, PartyAccepted, PartyApproval, PartyDropdown, PartyHistory,
                              PartyPending, PartyReject, Partydetails,PartyRejected, UpcomingParties)

urlpatterns = [
   path('request/',Party.as_view(),name='party-request'),
   path('details/',Partydetails.as_view(),name='party-details'),
   path('approval/<int:pk>/',PartyApproval.as_view(),name='party-approval'),
   path('reject/<int:pk>/',PartyReject.as_view(),name='party-approval'),
   path('approved/',PartyAccepted.as_view(),name='accepted-party'),
   path('pending/',PartyPending.as_view(),name='pending-party-status'),
   path('rejected/',PartyRejected.as_view(),name='rejected-party'),
   path('upcoming_party/',UpcomingParties.as_view(),name='upcoming-birthdays'),
   path('dropdown/',PartyDropdown.as_view(),name='party-dropdown'),
   path('give/',Give.as_view(),name='party-give'),
   path('graph/',Graph.as_view(),name='contribution-graph'),
   path('give_details/',AfterPartyDetails.as_view(),name='party-details'),
   path('<int:pk>/',AfterPartyImage.as_view(),name='party-images'),
   path('afterparty/status/<int:pk>/',AfterPartyApproval.as_view(),name='after-party-approval'),
   path('give_history/',GivePartyHistory.as_view(),name='give-history'),
   path('request_history/',PartyHistory.as_view(),name='party-request-history'),

  
 
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)