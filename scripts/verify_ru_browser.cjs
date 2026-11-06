async page => {
  await page.goto('http://127.0.0.1:8769/fonts/', {waitUntil: 'domcontentloaded'});
  await page.setViewportSize({width: 1200, height: 800});
  await page.setContent('<html lang="ru"><head><meta charset="utf-8"><link rel="icon" href="data:,"></head><body style="margin:40px;background:#f4f1e8;color:#262720"><h1 style="font:24px sans-serif">Departure Mono — браузерная проверка ударений</h1><main></main></body></html>');
  const results = await page.evaluate(async () => {
    const records = [];
    for (const format of ['otf', 'woff', 'woff2']) {
      for (const fixed of [false, true]) {
        const family = (fixed ? 'Fixed' : 'Original') + format;
        const path = fixed ? `/fonts/departure-mono-ru/DepartureMonoRU-Regular.${format}` : `/public/assets/DepartureMono-Regular.${format}`;
        const face = new FontFace(family, `url(${path})`);
        await face.load();
        document.fonts.add(face);
        const canvas = document.createElement('canvas');
        canvas.width = 100; canvas.height = 120;
        const context = canvas.getContext('2d', {willReadFrequently: true});
        context.font = `44px ${family}`;
        context.fillText('а\u0301', 0, 90);
        const width = context.measureText('а\u0301').width;
        const plainWidth = context.measureText('а').width;
        const pixels = context.getImageData(0, 0, 100, 65).data;
        const xs = [];
        for (let y = 0; y < 65; y++) for (let x = 0; x < 100; x++) {
          if (pixels[(y * 100 + x) * 4 + 3] > 128) xs.push(x);
        }
        if (!xs.length) throw new Error('Accent did not render: ' + family);
        const accentX = [Math.min(...xs), Math.max(...xs)];
        const expected = fixed ? [12, 19] : [40, 47];
        if (Math.abs(width - 28) > 0.05 || width !== plainWidth || accentX.some((v, i) => v !== expected[i])) {
          throw new Error(JSON.stringify({family, width, plainWidth, accentX, expected}));
        }
        const nfc = context.measureText('ЁёЙй').width;
        const nfd = context.measureText('Е\u0308е\u0308И\u0306и\u0306').width;
        if (nfc !== nfd) throw new Error('NFC/NFD width mismatch');
        for (const size of [11, 22, 33, 44]) {
          context.font = `${size}px ${family}`;
          if (Math.abs(context.measureText('за\u0301мок').width - 35 * size / 11) > 0.05) throw new Error('Word width changed');
        }
        const row = document.createElement('section');
        const label = document.createElement('p');
        label.style = 'font:14px sans-serif;margin:20px 0 10px';
        label.textContent = `${format.toUpperCase()} / ${fixed ? 'RU PROOF 1' : 'UPSTREAM 1.500'}`;
        const text = document.createElement('div');
        text.style = `font:44px ${family};line-height:1.4;font-synthesis:none`;
        text.textContent = 'за́мок  замо́к  молоко́  ПРИВЕ́Т';
        row.append(label, text);
        document.querySelector('main').append(row);
        records.push({family, loaded: face.status, width, accentX, nfcNfdEqual: nfc === nfd});
      }
    }
    return {browser: navigator.userAgent, devicePixelRatio, results: records};
  });
  await page.screenshot({path: 'docs/proofs/browser-stress.png', fullPage: true});
  return results;
}
