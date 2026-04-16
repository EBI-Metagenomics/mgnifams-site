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

const loadMGnifamsTable = () => {
  const tableEl = document.getElementById('mgnifams-table');
  const dataUrl = tableEl.dataset.url;
  const detailsPrefix = tableEl.dataset.detailsPrefix;
  const overlay = document.getElementById('loading-overlay');
  const infoBox = document.getElementById('filter-info-box');
  const applyBtn = document.getElementById('apply-filters-btn');

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
      overlay.classList.add('active');
      overlay.setAttribute('aria-hidden', 'false');
    })
    .on('xhr.dt', () => {
      overlay.classList.remove('active');
      overlay.setAttribute('aria-hidden', 'true');
    });

  applyBtn.addEventListener('click', () => {
    updateInfoBox();
    mgnifamsTable.draw();
  });
};

$(document).ready(() => {
  loadMGnifamsTable();
});
