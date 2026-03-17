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
        data: 0,
        render: (data) => `<a href="${detailsPrefix}${data}/">${data}</a>`,
      },
      { data: 1 },
      { data: 2 },
      { data: 3 },
      { data: 4 },
      { data: 5 },
      { data: 6 },
      { data: 7 },
      { data: 8 },
      { data: 9 },
      { data: 10 },
      { data: 11 },
    ],
  });

  $('#filters input').on('keyup change', () => {
    mgnifamsTable.draw();
  });
};

$(document).ready(() => {
  loadMGnifamsTable();
});
