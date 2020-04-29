from django.core.cache import caches, InvalidCacheBackendError


def clear_default_cache(sender, **kwargs):
    try:
        caches['default'].clear()
    except InvalidCacheBackendError:
        pass
