"""Clan queries: read the release's clan tables per request (never cached, so a DB swap shows at once)."""

from explorer.models import MgnifamClan, MgnifamClanEdge

ALMOST_DUPLICATE_JACCARD = 0.95
CLAN_LINK_JACCARD = 0.5


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
