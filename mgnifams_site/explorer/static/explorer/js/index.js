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
    const dataUrl = section.dataset.url;
    const detailsPrefix = section.dataset.detailsPrefix;
    const resultsBox = document.getElementById('annotation-results');
    const messageBox = document.getElementById('annotation-results-message');
    const input = document.getElementById('annotation-search');
    const overlay = document.getElementById('loading-overlay');

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

    const runAnnotationSearch = () => {
        const term = input.value.trim();

        if (!term) {
            resultsBox.classList.add('hidden');
            return;
        }

        if (term.length < MIN_QUERY_LENGTH) {
            resultsBox.classList.remove('hidden');
            $('#annotation-results-table').hide();
            setMessage('Please enter at least 4 characters to search.', 'annotation-results-error');
            return;
        }

        resultsBox.classList.remove('hidden');
        setMessage('', '');

        $('#annotation-results-table').show();
        if (annotationTable) {
            annotationTable.draw();
        } else {
            annotationTable = $('#annotation-results-table').DataTable({
                serverSide: true,
                searching: false,
                ajax: {
                    url: dataUrl,
                    data: (d) => { d.annotation_term = input.value.trim(); },
                },
                dom: 'iftplr',
                pageLength: 50,
                columns: [
                    { data: 'mgnifam_id', render: (data) => `<a href="${detailsPrefix}${data}/">${data}</a>` },
                    { data: 'full_size' },
                    { data: 'rep_length' },
                    { data: 'plddt' },
                    { data: 'ptm' },
                    { data: 'helix_percent' },
                    { data: 'strand_percent' },
                    { data: 'coil_percent' },
                    { data: 'inside_percent' },
                    { data: 'membrane_alpha_percent' },
                    { data: 'outside_percent' },
                    { data: 'signal_percent' },
                    { data: 'membrane_beta_percent' },
                    { data: 'periplasm_percent' },
                ],
            });
            annotationTable
                .on('preXhr.dt', () => {
                    overlay.classList.add('active');
                    overlay.setAttribute('aria-hidden', 'false');
                })
                .on('xhr.dt', () => {
                    overlay.classList.remove('active');
                    overlay.setAttribute('aria-hidden', 'true');
                });
        }
    };

    document.getElementById('annotation-search-btn').addEventListener('click', runAnnotationSearch);
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') runAnnotationSearch(); });
});
