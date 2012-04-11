from urllib import urlopen
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends import google


def update_user_details(backend, details, response, social_user, uid, user, *args, **kwargs):
#    import logging
#    logging.debug(type(backend))
#    logging.debug(type(response))
#    logging.debug(response)

    url = None
    if backend.__class__ == FacebookBackend:
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
        filename_prefix = 'facebook'
    elif backend.__class__ == TwitterBackend:
        url = response.get('profile_image_url', '').replace('_normal', '')
        filename_prefix = 'twitter'
    elif backend.__class__ == google.GoogleBackend:
        filename_prefix = 'google'
#        TODO: get google profile picture
#        try:
#            url = response.get('picture', None)
#        except Exception, ex:
#            logging.debug(str(ex))

    if url and not user.profile.photo:
        avatar = urlopen(url).read()
        user.profile.photo.save('avatars/%s%s.jpg' % (filename_prefix, response['id']), ContentFile(avatar))
