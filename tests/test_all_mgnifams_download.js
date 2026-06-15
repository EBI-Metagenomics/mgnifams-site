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
const currentPageMatch = source.match(/const currentPageHasAllFilteredRows = \(pageInfo, rowCount\) => \{[\s\S]*?\n\};/);
const queryStringMatch = source.match(/const buildQueryString = \(params\) => \{[\s\S]*?\n\};/);
const pageBlockingMatch = source.match(/const setPageBlocking = \(overlay, isBlocking\) => \{[\s\S]*?\n\};/);

assert(escapeMatch, 'escapeCsvValue function not found');
assert(buildMatch, 'buildMgnifamsCsv function not found');
assert(currentPageMatch, 'currentPageHasAllFilteredRows function not found');
assert(queryStringMatch, 'buildQueryString function not found');
assert(pageBlockingMatch, 'setPageBlocking function not found');

const context = { URLSearchParams };
vm.createContext(context);
vm.runInContext(
  [
    escapeMatch[0],
    buildMatch[0],
    currentPageMatch[0],
    queryStringMatch[0],
    pageBlockingMatch[0],
    'this.escapeCsvValue = escapeCsvValue;',
    'this.buildMgnifamsCsv = buildMgnifamsCsv;',
    'this.currentPageHasAllFilteredRows = currentPageHasAllFilteredRows;',
    'this.buildQueryString = buildQueryString;',
    'this.setPageBlocking = setPageBlocking;',
  ].join('\n'),
  context
);

assert.strictEqual(context.escapeCsvValue('plain'), 'plain');
assert.strictEqual(context.escapeCsvValue('contains,comma'), '"contains,comma"');
assert.strictEqual(context.escapeCsvValue('contains "quote"'), '"contains ""quote"""');
assert.strictEqual(context.escapeCsvValue(null), '');
assert.strictEqual(context.currentPageHasAllFilteredRows({ recordsDisplay: 3 }, 3), true);
assert.strictEqual(context.currentPageHasAllFilteredRows({ recordsDisplay: 51 }, 50), false);
assert.strictEqual(
  context.buildQueryString({
    draw: 1,
    order: [{ column: 0, dir: 'asc' }],
    search: { value: 'MGYF0000000001' },
    full_size_min: '',
  }),
  'draw=1&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&search%5Bvalue%5D=MGYF0000000001&full_size_min='
);

const overlay = {
  attributes: {},
  classList: {
    classes: new Set(),
    add(name) { this.classes.add(name); },
    remove(name) { this.classes.delete(name); },
    contains(name) { return this.classes.has(name); },
  },
  setAttribute(name, value) { this.attributes[name] = value; },
};
context.setPageBlocking(overlay, true);
assert.strictEqual(overlay.classList.contains('active'), true);
assert.strictEqual(overlay.attributes['aria-hidden'], 'false');
context.setPageBlocking(overlay, false);
assert.strictEqual(overlay.classList.contains('active'), false);
assert.strictEqual(overlay.attributes['aria-hidden'], 'true');

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
