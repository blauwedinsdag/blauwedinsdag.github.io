import sharp from 'sharp';
import { readdir, mkdir, readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';

// Originals stay untouched. Commit the variants so a normal Jekyll preview
// needs no image tools, and production deploys exactly the reviewed files.
const directory = 'images/optimized';
await mkdir(directory, { recursive: true });
await mkdir('_data', { recursive: true });
const manifest = {};
let originalBytes = 0;
let largestBytes = 0;
for (const filename of (await readdir('images')).sort()) {
  if (!/\.(jpe?g|png)$/i.test(filename)) continue;
  const src = `images/${filename}`;
  const input = await readFile(src);
  const image = sharp(input).autoOrient();
  const metadata = await image.metadata();
  const { width, height } = metadata.autoOrient;
  const variants = [];
  if (width >= 64) {
    const widths = [...new Set([320, 640, 960, 1440, Math.min(width, 1440)])]
      .filter(value => value <= width).sort((a, b) => a - b);
    for (const size of widths) {
      const url = `/${directory}/${filename.replaceAll('.', '-')}-${size}.webp`;
      const result = await image.clone().resize({ width: size, withoutEnlargement: true })
        .webp({ quality: 82, effort: 6, lossless: metadata.format === 'png' })
        .toFile(url.slice(1));
      variants.push({ width: result.width, url, bytes: result.size });
    }
    originalBytes += input.length;
    largestBytes += variants.at(-1).bytes;
  }
  manifest[`/${src}`] = {
    width, height,
    sha256: createHash('sha256').update(input).digest('hex'),
    variants,
  };
}
await writeFile('_data/images.json', `${JSON.stringify(manifest, null, 2)}\n`);
console.log(`Generated responsive variants for ${Object.values(manifest).filter(image => image.variants.length).length} images.`);
console.log(`Originals: ${(originalBytes / 1048576).toFixed(2)} MB; largest WebP variants: ${(largestBytes / 1048576).toFixed(2)} MB (${Math.round(100 * (1 - largestBytes / originalBytes))}% smaller).`);
