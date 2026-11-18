from explorer.releases import current_release


def release(request):
    return {'mgnifams_release': current_release(request)}
