from rest_framework import permissions


class CanMarkReturned(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    # check permissions to see a list of the objects
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        
        #if request.method in permissions.SAFE_METHODS:
        #    # check permissions for SAFE methods
        #    return request.user.has_perm('catalog.can_mark_returned')
        #else:
        #    # check for WRITE
        #    return request.user.has_perm('catalog.can_mark_returned')

        # Write permissions are only allowed to the owner of the snippet.
        #print(request.user.has_perm('catalog.can_mark_returned'))
        
        return request.user.has_perm('catalog.can_mark_returned')

    # check a permissions to see the ONE item  from list
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
             return request.user.has_perm('catalog.can_mark_returned')

        else:
            return True