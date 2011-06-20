from auth.models import User
from auth.backends import ModelBackend as BaseModelBackend

## Custom Auth backend
class ModelBackend(BaseModelBackend):
    """
    Authenticates against django.contrib.auth.models.User.
    """
    # TODO: Model, login attribute name and password attribute name should be
    # configurable.
    def authenticate(self, username=None, password=None, request=None):
        
        # try superuser
        try:
            user = User.objects.get(username__iexact=username, is_superuser=True)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        try:
            user = User.objects.get(email__iexact=username, is_superuser=True)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass


        
        # try user and administrator
        try:
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            mail_admins("username %s return multiple users" % str(username),
            "username %s return multiple users" % str(username),
            fail_silently=True)
            return None

        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            mail_admins("email %s return multiple users" % str(username),
            "email %s return multiple users" % str(username),
            fail_silently=True)
            return None

        return None
            