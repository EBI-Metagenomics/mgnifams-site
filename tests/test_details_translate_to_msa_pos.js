const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const detailsPath = path.join(
  __dirname,
  '..',
  'mgnifams_site',
  'explorer',
  'static',
  'explorer',
  'js',
  'details.js'
);

const source = fs.readFileSync(detailsPath, 'utf8');
const match = source.match(
  /const translate_to_msa_pos = \(sequence, hmm_position\) => \{[\s\S]*?\n\};/
);

assert(match, 'translate_to_msa_pos function not found');

const context = {};
vm.createContext(context);
vm.runInContext(`${match[0]}\nthis.translate_to_msa_pos = translate_to_msa_pos;`, context);

assert.strictEqual(context.translate_to_msa_pos('.xx.x.', 1), 0);
assert.strictEqual(context.translate_to_msa_pos('.xx.x.', 2), 1);
assert.strictEqual(context.translate_to_msa_pos('.xx.x.', 3), 3);
assert.strictEqual(context.translate_to_msa_pos('xx.x', 3), 3);
assert.strictEqual(context.translate_to_msa_pos('.xx.x.', 4), -1);

console.log('translate_to_msa_pos tests passed');
