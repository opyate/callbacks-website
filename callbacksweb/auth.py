from aiohttp import web
from aiohttp_session import SimpleCookieStorage, session_middleware
from aiohttp_security import check_permission, \
    is_anonymous, remember, forget, \
    setup as setup_security, SessionIdentityPolicy
from aiohttp_security.abc import AbstractAuthorizationPolicy


# Demo authorization policy for only one user.
# User 'jack' has only 'listen' permission.
# For more complicated authorization policies see examples
# in the 'demo' directory.
class SimpleJack_AuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        if identity == 'jack':
            return identity

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission
        in the current context, else return False.
        """
        return identity == 'jack' and permission in ('listen',)

