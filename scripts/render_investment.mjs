import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
let sharp;
try{sharp=require('sharp');}catch{sharp=require(require.resolve('sharp',{paths:[process.env.FTAI_GRAPHICS_NODE_MODULES??'C:/Users/vetsa/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules']}));}
await sharp(fs.readFileSync('public/graphics/investment-before-monetization.svg'),{density:144}).resize(2400,1640).png().toFile('public/graphics/investment-before-monetization.png');
console.log('Investment slide PNG rendered.');
