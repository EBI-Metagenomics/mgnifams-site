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
});
