// Convert the source-native SVG chart into a 2x slide PNG using bundled Sharp.
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
let sharp;
try{sharp=require('sharp');}catch{
 const root=process.env.FTAI_GRAPHICS_NODE_MODULES??'C:/Users/vetsa/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
 sharp=require(require.resolve('sharp',{paths:[root]}));
}
const svg=fs.readFileSync('public/graphics/power-gap-audit.svg');
await sharp(svg,{density:144}).resize(2400,1520).png().toFile('public/graphics/power-gap-audit.png');
console.log('Rendered 2400 x 1520 slide PNG.');
