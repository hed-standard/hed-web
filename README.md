# hed-web

Browser-based HED (Hierarchical Event Descriptor) validation tools.

This app consumes the [`hed-validator`](https://www.npmjs.com/package/hed-validator) npm package and provides two validation tools:

- **Validate dataset** — upload a BIDS dataset folder and check it for HED errors
- **Validate file** — validate a BIDS-style TSV file against its JSON sidecar

Live site: <https://hed-standard.github.io/hed-web/>

API docs: <https://hed-standard.github.io/hed-javascript/>

## Development

```powershell
npm install
npm run dev
```

Open the URLs printed by Vite (typically `http://localhost:5173/`).

## Build

```powershell
npm run build
npm run preview   # serves the production build under /hed-web/
```

Output goes to `buildweb/`.

## Tests

```powershell
npm test
```

Runs Vitest over `src/**/*.spec.{js,jsx}`.

## License

MIT — see [LICENSE](LICENSE).
