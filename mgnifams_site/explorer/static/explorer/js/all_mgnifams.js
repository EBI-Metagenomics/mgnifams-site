const loadMGnifamsTable = () => {
  let mgnifamsTable = $("#mgnifams-table").DataTable({
    dom: "iftplr",
    pageLength: 50,
    language: { searchPlaceholder: "Search", search: "" },
  });

  // Custom filtering function
  $.fn.dataTable.ext.search.push((settings, data, dataIndex) => {
    // Column values (skip ID at index 0)
    const colValues = {
      full_size: parseFloat(data[1]) || 0,
      rep_length: parseFloat(data[2]) || 0,
      helix: parseFloat(data[3]) || 0,
      strand: parseFloat(data[4]) || 0,
      coil: parseFloat(data[5]) || 0,
      inside: parseFloat(data[6]) || 0,
      membrane_alpha: parseFloat(data[7]) || 0,
      outside: parseFloat(data[8]) || 0,
      signal: parseFloat(data[9]) || 0,
      membrane_beta: parseFloat(data[10]) || 0,
      periplasm: parseFloat(data[11]) || 0,
    };

    // Filter inputs
    const filters = {
      full_size: [
        parseFloat($("#full_size_min").val()) || 1,
        parseFloat($("#full_size_max").val()) || Infinity
      ],
      rep_length: [
        parseFloat($("#rep_length_min").val()) || 1,
        parseFloat($("#rep_length_max").val()) || Infinity
      ],
      helix: [
        parseFloat($("#helix_min").val()) || 0,
        parseFloat($("#helix_max").val()) || 100
      ],
      strand: [
        parseFloat($("#strand_min").val()) || 0,
        parseFloat($("#strand_max").val()) || 100
      ],
      coil: [
        parseFloat($("#coil_min").val()) || 0,
        parseFloat($("#coil_max").val()) || 100
      ],
      inside: [
        parseFloat($("#inside_min").val()) || 0,
        parseFloat($("#inside_max").val()) || 100
      ],
      membrane_alpha: [
        parseFloat($("#membrane_alpha_min").val()) || 0,
        parseFloat($("#membrane_alpha_max").val()) || 100
      ],
      outside: [
        parseFloat($("#outside_min").val()) || 0,
        parseFloat($("#outside_max").val()) || 100
      ],
      signal: [
        parseFloat($("#signal_min").val()) || 0,
        parseFloat($("#signal_max").val()) || 100
      ],
      membrane_beta: [
        parseFloat($("#membrane_beta_min").val()) || 0,
        parseFloat($("#membrane_beta_max").val()) || 100
      ],
      periplasm: [
        parseFloat($("#periplasm_min").val()) || 0,
        parseFloat($("#periplasm_max").val()) || 100
      ],
    };

    // Check each column against min/max
    for (const col in colValues) {
      if (
        colValues[col] < filters[col][0] ||
        colValues[col] > filters[col][1]
      ) {
        return false;
      }
    }

    return true;
  });

  // Redraw on input change
  $("#filters input").on("keyup change", () => {
    mgnifamsTable.draw();
  });
};

$(document).ready(() => {
  loadMGnifamsTable();
});