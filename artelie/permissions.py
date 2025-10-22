from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão customizada para permitir apenas o próprio usuário ou admin.
    BENEFÍCIO: Proteção granular de recursos.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin tem acesso total
        if request.user and request.user.is_staff:
            return True
        
        # Usuário pode acessar apenas seus próprios dados
        return obj == request.user


class IsVerifiedUser(permissions.BasePermission):
    """
    Permissão que exige que o usuário tenha email verificado.
    BENEFÍCIO: Garante que apenas usuários verificados acessem recursos.
    """
    
    message = 'Você precisa verificar seu email antes de acessar este recurso.'
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )
