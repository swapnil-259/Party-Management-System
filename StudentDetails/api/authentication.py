from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from rest_framework.permissions import IsAuthenticated,BasePermission
class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return
    

class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
       if request.user.is_authenticated:
           return True
       else :
           return False