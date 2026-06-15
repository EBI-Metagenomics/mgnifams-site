const ANNOTATION_FILTER_NAMES = ['has_pfam', 'has_funfam', 'has_model_pfam', 'has_structure'];

const ANNOTATION_FILTER_LABELS = {
  has_pfam:        'Pfam hits',
  has_funfam:      'FunFam hits',
  has_model_pfam:  'Profile-Pfam hits',
  has_structure:   'Structure hits',
};

const FILTER_LABELS = {
  full_size_min:       'Full size ≥',
  full_size_max:       'Full size ≤',
  rep_length_min:      'Rep. length ≥',
  rep_length_max:      'Rep. length ≤',
  plddt_min:           'pLDDT ≥',
  plddt_max:           'pLDDT ≤',
  ptm_min:             'pTM ≥',
  ptm_max:             'pTM ≤',
  helix_min:           'Helix% ≥',
  helix_max:           'Helix% ≤',
  strand_min:          'Strand% ≥',
  strand_max:          'Strand% ≤',
  coil_min:            'Coil% ≥',
  coil_max:            'Coil% ≤',
  inside_min:          'Inside% ≥',
  inside_max:          'Inside% ≤',
  membrane_alpha_min:  'Membrane-alpha% ≥',
  membrane_alpha_max:  'Membrane-alpha% ≤',
  outside_min:         'Outside% ≥',
  outside_max:         'Outside% ≤',
  signal_min:          'Signal% ≥',
  signal_max:          'Signal% ≤',
  membrane_beta_min:   'Membrane-beta% ≥',
  membrane_beta_max:   'Membrane-beta% ≤',
  periplasm_min:       'Periplasm% ≥',
  periplasm_max:       'Periplasm% ≤',
};

const escapeCsvValue = (value) => {
  if (value === null || value === undefined) {
    return '';
  }
  const text = String(value);
  if (/[",\n\r]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
};

const buildMgnifamsCsv = (rows) => {
  const headers = [
    'ID', 'Full size', 'Representative length', 'pLDDT', 'pTM', 'Helix%', 'Strand%', 'Coil%', 'Inside%',
    'Membrane-alpha%', 'Outside%', 'Signal%', 'Membrane-beta%', 'Periplasm%',
  ];
  const fields = [
    'mgnifam_id', 'full_size', 'rep_length', 'plddt', 'ptm', 'helix_percent', 'strand_percent', 'coil_percent',
    'inside_percent', 'membrane_alpha_percent', 'outside_percent', 'signal_percent', 'membrane_beta_percent',
    'periplasm_percent',
  ];
  const lines = rows.map((row) => fields.map((field) => escapeCsvValue(row[field])).join(','));
  return [headers.join(','), ...lines].join('\n');
};

const currentPageHasAllFilteredRows = (pageInfo, rowCount) => {
  return pageInfo.recordsDisplay === rowCount;
};

const buildQueryString = (params) => {
  const searchParams = new URLSearchParams();

  function appendValue(key, value) {
    if (value === undefined || value === null) {
      return;
    }
    if (Array.isArray(value)) {
      for (let i = 0; i < value.length; i++) {
        appendValue(`${key}[${i}]`, value[i]);
      }
      return;
    }
    if (typeof value === 'object') {
      for (const nestedKey of Object.keys(value)) {
        appendValue(`${key}[${nestedKey}]`, value[nestedKey]);
      }
      return;
    }
    searchParams.append(key, value);
  }

  for (const key of Object.keys(params)) {
    appendValue(key, params[key]);
  }
  return searchParams.toString();
};

const setPageBlocking = (overlay, isBlocking) => {
  // Share one overlay path for table loads and CSV work so users cannot trigger competing requests.
  overlay.classList[isBlocking ? 'add' : 'remove']('active');
  overlay.setAttribute('aria-hidden', isBlocking ? 'false' : 'true');
};

const downloadTextFile = (filename, text) => {
  const blob = new Blob([text], { type: 'text/csv;charset=utf-8;' });
  downloadBlobFile(filename, blob);
};

const downloadBlobFile = (filename, blob) => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

const loadMGnifamsTable = () => {
  const tableEl = document.getElementById('mgnifams-table');
  const dataUrl = tableEl.dataset.url;
  const detailsPrefix = tableEl.dataset.detailsPrefix;
  const overlay = document.getElementById('loading-overlay');
  const infoBox = document.getElementById('filter-info-box');
  const applyBtn = document.getElementById('apply-filters-btn');
  const downloadBtn = document.getElementById('download-mgnifams-btn');

  const filterInputIds = [
    'full_size_min', 'full_size_max',
    'rep_length_min', 'rep_length_max',
    'plddt_min', 'plddt_max',
    'ptm_min', 'ptm_max',
    'helix_min', 'helix_max',
    'strand_min', 'strand_max',
    'coil_min', 'coil_max',
    'inside_min', 'inside_max',
    'membrane_alpha_min', 'membrane_alpha_max',
    'outside_min', 'outside_max',
    'signal_min', 'signal_max',
    'membrane_beta_min', 'membrane_beta_max',
    'periplasm_min', 'periplasm_max',
  ];

  let mgnifamsTable = $(tableEl).DataTable({
    serverSide: true,
    ajax: {
      url: dataUrl,
      data: function (d) {
        filterInputIds.forEach((id) => {
          d[id] = $(`#${id}`).val();
        });
        ANNOTATION_FILTER_NAMES.forEach((name) => {
          d[name] = $(`input[name="${name}"]:checked`).val();
        });
      },
    },
    dom: 'iftplr',
    pageLength: 50,
    language: { searchPlaceholder: 'Search by ID', search: '' },
    columns: [
      {
        data: 'mgnifam_id',
        render: (data) => `<a href="${detailsPrefix}${data}/">${data}</a>`,
      },
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

  const updateInfoBox = () => {
    const parts = filterInputIds
      .filter((id) => $(`#${id}`).val().trim() !== '')
      .map((id) => `${FILTER_LABELS[id]} ${$(`#${id}`).val().trim()}`);
    ANNOTATION_FILTER_NAMES.forEach((name) => {
      const val = $(`input[name="${name}"]:checked`).val();
      if (val && val !== 'any') {
        parts.push(`${ANNOTATION_FILTER_LABELS[name]}: ${val}`);
      }
    });
    infoBox.textContent = parts.length
      ? 'Active filters: ' + parts.join(' | ')
      : 'No filters applied';
  };

  updateInfoBox();

  mgnifamsTable
    .on('preXhr.dt', () => {
      setPageBlocking(overlay, true);
    })
    .on('xhr.dt', () => {
      setPageBlocking(overlay, false);
    });

  applyBtn.addEventListener('click', () => {
    updateInfoBox();
    mgnifamsTable.draw();
  });

  downloadBtn.addEventListener('click', async () => {
    setPageBlocking(overlay, true);
    downloadBtn.disabled = true;
    downloadBtn.textContent = 'Preparing CSV';

    // With server-side DataTables, the browser only owns one page unless the filtered result fits there.
    const currentRows = mgnifamsTable.rows({ page: 'current' }).data().toArray();
    if (currentPageHasAllFilteredRows(mgnifamsTable.page.info(), currentRows.length)) {
      downloadTextFile('mgnifams.csv', buildMgnifamsCsv(currentRows));
      setPageBlocking(overlay, false);
      downloadBtn.disabled = false;
      downloadBtn.textContent = 'Download CSV';
      return;
    }

    // Larger exports go back to Django as streamed CSV while preserving the visible filters, search, and sort.
    const params = {
      ...mgnifamsTable.ajax.params(),
      start: 0,
      // length=-1 is our backend export convention; normal DataTables pagination remains unchanged.
      length: -1,
      draw: 1,
      export: 'csv',
    };
    try {
      const response = await fetch(`${dataUrl}?${buildQueryString(params)}`, { headers: { Accept: 'text/csv' } });
      if (!response.ok) {
        throw new Error(`CSV export failed with HTTP ${response.status}`);
      }
      downloadBlobFile('mgnifams.csv', await response.blob());
    } catch (error) {
      console.error('MGnifams CSV download failed:', error);
      window.alert('Could not download the MGnifams CSV. Please retry or narrow the filters.');
    } finally {
      setPageBlocking(overlay, false);
      downloadBtn.disabled = false;
      downloadBtn.textContent = 'Download CSV';
    }
  });
};

$(document).ready(() => {
  loadMGnifamsTable();
});
