document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('search-form');

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const id = document.getElementById('id').value.trim();
        if (id) {
            const detailsUrl = form.dataset.detailsUrl.replace('PROTID', encodeURIComponent(id));
            window.location.href = detailsUrl;
        }
    });

    document.getElementById('example-btn').addEventListener('click', () => {
        document.getElementById('id').value = form.dataset.firstId;
    });

    // Annotation search
    const section = document.getElementById('annotation-search-section');
    const searchUrl = section.dataset.searchUrl;
    const detailsPrefix = section.dataset.detailsPrefix.replace('PROTID/', '');
    const resultsBox = document.getElementById('annotation-results');
    const messageBox = document.getElementById('annotation-results-message');
    const input = document.getElementById('annotation-search');

    const MIN_QUERY_LENGTH = 4;
    let annotationTable = null;

    const escapeHtml = (str) => {
        const d = document.createElement('div');
        d.appendChild(document.createTextNode(str));
        return d.innerHTML;
    };

    const setMessage = (html, cssClass) => {
        messageBox.innerHTML = html ? `<p class="${cssClass}">${html}</p>` : '';
    };

    const showTable = (show) => {
        $('#annotation-results-table').toggle(show);
    };

    const runAnnotationSearch = async () => {
        const term = input.value.trim();

        if (!term) {
            resultsBox.classList.add('hidden');
            return;
        }

        resultsBox.classList.remove('hidden');

        if (term.length < MIN_QUERY_LENGTH) {
            setMessage('Please enter at least 4 characters to search.', 'annotation-results-error');
            showTable(false);
            return;
        }

        setMessage('Searching…', 'annotation-results-loading');

        try {
            const response = await fetch(`${searchUrl}?term=${encodeURIComponent(term)}`);
            const data = await response.json();
            renderAnnotationResults(data, term);
        } catch {
            setMessage('Search failed. Please try again.', 'annotation-results-error');
            showTable(false);
        }
    };

    const renderAnnotationResults = (data, term) => {
        if (data.count === 0) {
            setMessage(`No families found for <em>${escapeHtml(term)}</em>.`, 'annotation-results-empty');
            showTable(false);
            return;
        }

        setMessage(
            `${data.count} famil${data.count === 1 ? 'y' : 'ies'} found for <em>${escapeHtml(term)}</em>:`,
            'annotation-results-header'
        );

        const rows = data.results.map((r) => [
            `<a href="${detailsPrefix}${r.mgnifam_id}/">${r.mgnifam_id}</a>`,
            r.full_size,
            r.rep_length,
            r.plddt,
            r.ptm,
            r.helix_percent,
            r.strand_percent,
            r.coil_percent,
            r.inside_percent,
            r.membrane_alpha_percent,
            r.outside_percent,
            r.signal_percent,
            r.membrane_beta_percent,
            r.periplasm_percent,
        ]);

        showTable(true);
        if (annotationTable) {
            annotationTable.clear().rows.add(rows).draw();
        } else {
            annotationTable = $('#annotation-results-table').DataTable({
                data: rows,
                dom: 'iftplr',
                pageLength: 50,
                language: { searchPlaceholder: 'Filter results', search: '' },
            });
        }
    };

    document.getElementById('annotation-search-btn').addEventListener('click', runAnnotationSearch);
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') runAnnotationSearch(); });
});
