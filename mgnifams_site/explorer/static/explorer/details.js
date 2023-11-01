const stringToHexColor = (str) => {
  let color = '';

  if (str.length === 1) {
    const charCode = str.charCodeAt(0);

    const red = (charCode * 13) % 256;
    const green = (charCode * 17) % 256;
    const blue = (charCode * 19) % 256;

    const redHex = red.toString(16).padStart(2, '0');
    const greenHex = green.toString(16).padStart(2, '0');
    const blueHex = blue.toString(16).padStart(2, '0');

    color = `#${redHex}${greenHex}${blueHex}`;

    return color;
  }

  let hash = 0;

  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }

  color = '#';

  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xff;
    color += value.toString(16).padStart(2, '0');
  }

  return color;
};

const extractProteinIdFromUrl = () => {
  const url = window.location.href;
  const parts = url.split('/');
  const preLastPart = parts[parts.length - 2];

  return preLastPart;
};

document.addEventListener('DOMContentLoaded', () => {
//   const viewerInstance = new PDBeMolstarPlugin();
//   const viewerContainer = document.getElementById('pdb_viewer');
//   const proteinId = extractProteinIdFromUrl();

//   const options = {
//     customData: {
//       url: `/${proteinId}/structure`,
//       format: 'pdb',
//     },
//     bgColor: { r: 252, g: 251, b: 249 },
//     hideControls: true,
//     sequencePanel: true,
//     landscape: true,
//   };

//   viewerInstance.render(viewerContainer, options);

//   document
//     .getElementById('my_nightingale_manager')
//     .addEventListener('click', (e) => {
//       const { __data__: data } = e.target;

//       if (!data) return;

//       if (data.feature) {
//         viewerInstance.visual.select({
//           data: [
//             {
//               struct_asym_id: 'A',
//               start_residue_number: data.feature.start,
//               end_residue_number: data.feature.end,
//               color: data.feature.color,
//               focus: true,
//             },
//           ],
//         });
//       }

//       if (data.aa) {
//         viewerInstance.visual.select({
//           data: [
//             {
//               struct_asym_id: 'A',
//               start_residue_number: data.position,
//               end_residue_number: data.position,
//               color: stringToHexColor(data.aa),
//               focus: true,
//             },
//           ],
//         });
//       }
//     });

//   document
//     .getElementById('my-nightingale-sequence-id')
//     .addEventListener('mouseover', (e) => {
//       const { __data__: data } = e.target;

//       if (!data) return;

//       viewerInstance.visual.highlight({
//         data: [
//           {
//             struct_asym_id: 'A',
//             start_residue_number: data.position,
//             end_residue_number: data.position,
//             color: stringToHexColor(data.aa),
//             focus: true,
//           },
//         ],
//       });
//     });

//   const nightingaleNavigation = document.getElementById('my_navigation');
//   const nightingaleSequence = document.getElementById(
//     'my-nightingale-sequence-id'
//   );
//   const nightingaleTrack = document.getElementById('my_track_id');

//   document.addEventListener('PDB.molstar.click', (e) => {
//     nightingaleNavigation.locate(
//       e.eventData.seq_id - 50,
//       e.eventData.seq_id + 50
//     );
//   });

//   document.addEventListener('PDB.molstar.mouseover', (e) => {
//     const position = e.eventData.seq_id;
//     nightingaleSequence.highlight = `${position}:${position}`;
//     nightingaleNavigation.highlight = `${position}:${position}`;
//     nightingaleTrack.highlight = `${position}:${position}`;
//   });

  document.getElementById('copy_button').addEventListener('click', () => {
    const sequence = document.getElementById('protein_sequence').innerText;
    const button = document.getElementById('copy_button');

    navigator.clipboard.writeText(sequence).then(
      () => {
        button.textContent = 'Copied to clipboard';
        button.disabled = true;

        setTimeout(() => {
          button.textContent = 'Copy';
          button.disabled = false;
        }, 3000);
      },
      () => {
        button.textContent = 'Failed to copy';
      }
    );
  });
});

$(document).ready(() => {
  if ($('#pfams-table:contains("No Pfam domains found")').length === 0) {
    $('#pfams-table').DataTable({
      dom: 'iftplr',
      language: {
        searchPlaceholder: 'Search',
        search: '',
      },
    });
  }

  if ($('#assembly-table:contains("No assemblies found")').length === 0) {
    $('#assembly-table').DataTable();
  }

  const items = document.getElementsByClassName('pfam-item');

  for (let i = 0; i < items.length; i++) {
    const proteinPfamId = items[i].dataset.proteinpfam;
    const bgColor = stringToHexColor(proteinPfamId);
    const fourthCell = items[i].querySelector('td:nth-child(4)');

    fourthCell.style.backgroundColor = bgColor;
  }
});
