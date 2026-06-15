const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const allMgnifamsPath = path.join(
  __dirname,
  '..',
  'mgnifams_site',
  'explorer',
  'static',
  'explorer',
  'js',
  'all_mgnifams.js'
);

const source = fs.readFileSync(allMgnifamsPath, 'utf8');
const escapeMatch = source.match(/const escapeCsvValue = \(value\) => \{[\s\S]*?\n\};/);
const buildMatch = source.match(/const buildMgnifamsCsv = \(rows\) => \{[\s\S]*?\n\};/);

assert(escapeMatch, 'escapeCsvValue function not found');
assert(buildMatch, 'buildMgnifamsCsv function not found');

const context = {};
vm.createContext(context);
vm.runInContext(
  `${escapeMatch[0]}\n${buildMatch[0]}\nthis.escapeCsvValue = escapeCsvValue;this.buildMgnifamsCsv = buildMgnifamsCsv;`,
  context
);

assert.strictEqual(context.escapeCsvValue('plain'), 'plain');
assert.strictEqual(context.escapeCsvValue('contains,comma'), '"contains,comma"');
assert.strictEqual(context.escapeCsvValue('contains "quote"'), '"contains ""quote"""');
assert.strictEqual(context.escapeCsvValue(null), '');

const csv = context.buildMgnifamsCsv([
  {
    mgnifam_id: 'MGYF0000000001',
    full_size: 100,
    rep_length: 80,
    plddt: 85.5,
    ptm: 0.9,
    helix_percent: 30,
    strand_percent: 20,
    coil_percent: 50,
    inside_percent: 10,
    membrane_alpha_percent: 5,
    outside_percent: 75,
    signal_percent: 5,
    membrane_beta_percent: 3,
    periplasm_percent: 2,
  },
]);

assert.strictEqual(
  csv,
  [
    'ID,Full size,Representative length,pLDDT,pTM,Helix%,Strand%,Coil%,Inside%,Membrane-alpha%,Outside%,Signal%,Membrane-beta%,Periplasm%',
    'MGYF0000000001,100,80,85.5,0.9,30,20,50,10,5,75,5,3,2',
  ].join('\n')
);

console.log('all_mgnifams download tests passed');
