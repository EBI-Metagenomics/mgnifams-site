def format_family_name(id):
    """
    Formats the mgnifam name by appending zeros in front to make it 10 characters,
    and then adds 'MGYF' as a prefix.
    """
    if id is None:
        return ''
    return 'MGYF' + str(id).zfill(10)
