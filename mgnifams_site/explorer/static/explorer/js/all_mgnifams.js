const loadMGnifamsTable = () => {
  let mgnifamsTable = $("#mgnifams-table").DataTable({
    dom: "iftplr",
    pageLength: 50,
    language: {
        searchPlaceholder: "Search",
        search: "",
    },
  });
};

$(document).ready(() => {
  loadMGnifamsTable();
});
