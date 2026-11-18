"""Clan queries: read the release's clan tables per request (never cached, so a DB swap shows at once)."""

from django.db import connection
from django.db.models import F

from explorer.models import MgnifamClan, MgnifamClanEdge

ALMOST_DUPLICATE_JACCARD = 0.95
CLAN_LINK_JACCARD = 0.5
PAGE_SIZE = 50


def _family_pairs(family_id):
    """(other family ID, residue Jaccard) of every stored pair of the family; one indexed lookup per direction."""
    as_first = MgnifamClanEdge.objects.filter(family_1=family_id).values_list('family_2', 'residue_jaccard')
    as_second = MgnifamClanEdge.objects.filter(family_2=family_id).values_list('family_1', 'residue_jaccard')
    return [*as_first, *as_second]


def family_clan_summary(family_id):
    clan = MgnifamClan.objects.filter(mgnifam_id=family_id).first()
    clan_size = MgnifamClan.objects.filter(clan_id=clan.clan_id).count() if clan else 0
    # Highest Jaccard first, ties to the lower family ID; a pair with no Jaccard is neither duplicate nor closest.
    pairs = sorted(
        ((other, jaccard) for other, jaccard in _family_pairs(family_id) if jaccard is not None),
        key=lambda pair: (-pair[1], pair[0]),
    )
    return {
        'clan_id': clan.clan_id if clan else None,
        'clan_size': clan_size,
        'is_representative': bool(clan and clan.is_representative),
        'duplicates': [other for other, jaccard in pairs if jaccard >= ALMOST_DUPLICATE_JACCARD],
        'closest': {'family_id': pairs[0][0], 'residue_jaccard': pairs[0][1]} if pairs else None,
    }


def clan_members(clan_id):
    """Every member of the clan with its list columns, representative first; empty for an unknown clan."""
    columns = ['full_size', 'rep_length', 'status', 'has_pfam', 'has_funfam', 'has_structure']
    rows = MgnifamClan.objects.filter(clan_id=clan_id).values(
        'is_representative', 'mgnifam_id', *(f'mgnifam__{column}' for column in columns)
    )
    members = [
        {
            'family_id': row['mgnifam_id'],
            'is_representative': row['is_representative'],
            **{column: row[f'mgnifam__{column}'] for column in columns},
        }
        for row in rows
    ]
    return sorted(members, key=lambda member: (not member['is_representative'], member['family_id']))


def _inside_pairs(member_ids):
    return MgnifamClanEdge.objects.filter(family_1__in=member_ids, family_2__in=member_ids)


def clan_pairs(member_ids, requested_page):
    """One page of the stored pairs inside the clan, highest residue Jaccard first (see _page)."""
    pairs = _inside_pairs(member_ids)
    page = _page(pairs.count(), requested_page)
    rows = pairs.order_by(F('residue_jaccard').desc(nulls_last=True), 'family_1', 'family_2').values(
        'family_1', 'family_2', 'residue_jaccard', 'residue_containment', 'shared_proteins'
    )
    page['rows'] = list(rows[page['offset'] : page['offset'] + PAGE_SIZE])
    return page


def clan_duplicate_pairs(member_ids):
    return _inside_pairs(member_ids).filter(residue_jaccard__gte=ALMOST_DUPLICATE_JACCARD).count()


# Pairs between a member (in the members CTE) and a family outside the clan, as (outside, member, ...).
_OUTSIDE_PAIRS = """
WITH members(id) AS (VALUES {values}),
pairs AS (
    SELECT family_2 AS outside, family_1 AS member, residue_jaccard, residue_containment, shared_proteins
    FROM mgnifam_clan_edges
    WHERE family_1 IN (SELECT id FROM members) AND family_2 NOT IN (SELECT id FROM members)
    UNION ALL
    SELECT family_1, family_2, residue_jaccard, residue_containment, shared_proteins
    FROM mgnifam_clan_edges
    WHERE family_2 IN (SELECT id FROM members) AND family_1 NOT IN (SELECT id FROM members)
)
"""

# One row per outside family: its best pair (highest residue Jaccard, ties to the lower member ID).
# "x IS NULL" sorts NULL last on any SQLite with window functions, which NULLS LAST would not.
_OUTSIDE_PAGE = """
, ranked AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY outside ORDER BY residue_jaccard IS NULL, residue_jaccard DESC, member
    ) AS n
    FROM pairs
)
SELECT ranked.outside, mgnifam_clans.clan_id, ranked.member,
       ranked.residue_jaccard, ranked.residue_containment, ranked.shared_proteins
FROM ranked LEFT JOIN mgnifam_clans ON mgnifam_clans.mgnifam_id = ranked.outside
WHERE ranked.n = 1
ORDER BY ranked.residue_jaccard IS NULL, ranked.residue_jaccard DESC, ranked.outside
LIMIT %s OFFSET %s
"""


def outside_families(member_ids, requested_page):
    """One page of the families outside the clan with a stored pair to a member, each with its best pair."""
    pairs = _OUTSIDE_PAIRS.format(values=', '.join(['(%s)'] * len(member_ids)))
    with connection.cursor() as cursor:
        cursor.execute(pairs + 'SELECT COUNT(DISTINCT outside) FROM pairs', member_ids)
        page = _page(cursor.fetchone()[0], requested_page)
        cursor.execute(pairs + _OUTSIDE_PAGE, [*member_ids, PAGE_SIZE, page['offset']])
        keys = ['family_id', 'clan_id', 'member_id', 'residue_jaccard', 'residue_containment', 'shared_proteins']
        page['rows'] = [dict(zip(keys, row, strict=True)) for row in cursor.fetchall()]
    return page


def _page_number(value, total, per_page=PAGE_SIZE):
    """The requested page, clamped to the pages there are; anything that is not a number is page 1."""
    last = max(1, -(-total // per_page))
    try:
        page = int(value)
    except (TypeError, ValueError):
        return 1
    return min(max(page, 1), last)


def _page(total, requested_page):
    """Paging facts of a table of `total` rows for the page asked for in the URL (a string, or None)."""
    number = _page_number(requested_page, total)
    return {'total': total, 'page': number, 'pages': max(1, -(-total // PAGE_SIZE)), 'offset': (number - 1) * PAGE_SIZE}
