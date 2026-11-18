import re

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


# Download URL of each searched database, built from its version number.
_VERSIONED_URLS = {
    'pfam': ('databases.pfam', 'https://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam{v}/Pfam-A.hmm.gz'),
    'pfam_profile_profile': (
        'databases.pfam_profile_profile',
        'https://wwwuser.gwdguser.de/~compbiol/data/hhsuite/databases/hhsuite_dbs/pfamA_{v}.tar.gz',
    ),
    'funfams': (
        'databases.funfams',
        'https://download.cathdb.info/cath/releases/all-releases/v{u}/sequence-data/funfam-hmm3-v{u}.lib.gz',
    ),
}

_FOLDSEEK_PARTS = [
    ('Foldseek {}', ['databases.foldseek.search_version']),
    ('PDB ({}, {})', ['databases.foldseek.pdb.database', 'databases.foldseek.pdb.pdb_date']),
    (
        'AlphaFold DB ({}, {})',
        ['databases.foldseek.alphafold_db.database', 'databases.foldseek.alphafold_db.version'],
    ),
]


def _version_number(value):
    match = re.fullmatch(r'\D*?v?(\d+(?:\.\d+)+)', value or '')
    return match.group(1) if match else None


def version_labels(info):
    """Database version labels for the details page from a release's release_info.

    A missing or unparsable value gives an empty label, never a guessed version.
    """
    labels = {}
    for name, (key, url) in _VERSIONED_URLS.items():
        number = _version_number(info.get(key))
        labels[name] = (
            {'text': f'ver. {number}', 'url': url.format(v=number, u=number.replace('.', '_'))}
            if number
            else {'text': '', 'url': None}
        )
    search, pdb, afdb = (
        template.format(*values) if all(values := [info.get(key) for key in keys]) else ''
        for template, keys in _FOLDSEEK_PARTS
    )
    text = '; '.join(filter(None, [search, ' and '.join(filter(None, [pdb, afdb]))]))
    labels['foldseek'] = {'text': text, 'url': None}
    return labels
