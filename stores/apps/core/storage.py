from django.conf import settings
from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage

STATIC_STORAGE_BUCKET_NAME=getattr(settings, 'AWS_STATIC_BUCKET_NAME', None) 

class CachedS3BotoStorage(S3BotoStorage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        name = super(CachedS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name
    
class StaticS3BotoStorage(S3BotoStorage):
    """Amazon Simple Storage Service using Boto"""
    def __init__(self, bucket=STATIC_STORAGE_BUCKET_NAME, * args, ** kwargs):        
        return super(StaticS3BotoStorage, self).__init__(bucket=bucket, *args, ** kwargs)

class CachedStaticS3BotoStorage(StaticS3BotoStorage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        super(CachedStaticS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        name = super(CachedStaticS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name

