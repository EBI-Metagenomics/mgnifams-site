from explorer.models import ReleaseHistory, ReleaseInfo


def _version_key(row):
    return tuple(int(part) for part in row.release.split('.'))


def current_release(request=None):
    """The latest release_history row and its release_info as a dict, or None.

    Read on the request's own connection and memoized on the request only, never across requests,
    so a swapped DB file is never described by values read from the old one.
    """
    if request is not None and hasattr(request, '_mgnifams_release'):
        return request._mgnifams_release
    rows = list(ReleaseHistory.objects.only('release', 'date'))
    release = None
    if rows:
        latest = max(rows, key=_version_key)
        info = dict(ReleaseInfo.objects.filter(release=latest.release).values_list('key', 'value'))
        release = {'release': latest.release, 'date': latest.date, 'info': info}
    if request is not None:
        request._mgnifams_release = release
    return release
