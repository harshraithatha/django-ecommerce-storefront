import os

from django.conf import settings
from django.dispatch import receiver
from django_cleanup.signals import cleanup_post_delete


@receiver(cleanup_post_delete)
def remove_empty_dirs(sender, **kwargs):
    """Prune now-empty directories after django-cleanup removes a file.

    django-cleanup only deletes files, so a deleted product can leave behind
    empty ``products/<slug>/original/`` and ``thumbs/`` folders. This fires
    once per deleted file (after the file is actually gone) and climbs upward,
    removing each empty directory until it hits a non-empty one or MEDIA_ROOT.

    Note: by the time this fires, ``FieldFile.delete()`` has already reset the
    file object's ``name`` to ``None``, so we rely on the ``file_name`` the
    signal carries rather than ``file.name``.
    """
    if not kwargs.get('success'):
        return

    file_ = kwargs.get('file')
    file_name = kwargs.get('file_name')
    if file_ is None or not file_name:
        return

    try:
        path = file_.storage.path(file_name)
    except (NotImplementedError, ValueError, AttributeError):
        # Non-filesystem storage (e.g. S3) has no local path to prune.
        return

    media_root = os.path.abspath(settings.MEDIA_ROOT)
    directory = os.path.dirname(os.path.abspath(path))

    while directory != media_root and directory.startswith(media_root + os.sep):
        try:
            os.rmdir(directory)  # raises OSError unless the directory is empty
        except OSError:
            break
        directory = os.path.dirname(directory)
