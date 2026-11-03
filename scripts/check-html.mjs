import { HtmlValidate } from 'html-validate';
import { readdir } from 'node:fs/promises';
import path from 'node:path';

async function files(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map(entry => {
    const filename = path.join(directory, entry.name);
    return entry.isDirectory() ? files(filename) : filename.endsWith('.html') ? [filename] : [];
  }));
  return nested.flat();
}

const validator = new HtmlValidate({ extends: ['html-validate:standard'] });
const pages = await files(process.env.SITE_DIR || '_site');
if (!pages.length) throw new Error('No generated pages found. Build Jekyll first.');
let errors = 0;
for (const filename of pages) {
  const report = await validator.validateFile(filename);
  if (!report.valid) {
    for (const result of report.results) {
      for (const message of result.messages) {
        console.error(`${filename}:${message.line}:${message.column}: ${message.message} (${message.ruleId})`);
        errors += 1;
      }
    }
  }
}
if (errors) process.exit(1);
console.log(`HTML validation passed for ${pages.length} pages.`);
