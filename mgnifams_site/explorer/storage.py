from whitenoise.storage import CompressedManifestStaticFilesStorage


class ManifestOptionalStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """
    Whitenoise storage with manifest_strict=False so that missing or not-yet-built
    manifests don't raise errors in development or tests.  In production, after
    `collectstatic` is run, files are served with content-hash cache-busting and
    gzip/brotli compression as normal.
    """

    manifest_strict = False
