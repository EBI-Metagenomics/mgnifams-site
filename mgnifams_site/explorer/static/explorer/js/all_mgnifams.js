const loadMGnifamsTable = () => {
  const tableEl = document.getElementById('mgnifams-table');
  const dataUrl = tableEl.dataset.url;
  const detailsPrefix = tableEl.dataset.detailsPrefix;

  const filterInputIds = [
    'full_size_min', 'full_size_max',
    'rep_length_min', 'rep_length_max',
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

  $('#filters input').on('keyup change', () => {
    mgnifamsTable.draw();
  });
};

$(document).ready(() => {
  loadMGnifamsTable();
});
