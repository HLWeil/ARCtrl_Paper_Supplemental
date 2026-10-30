import { readFileSync, writeFileSync } from "node:fs";
import { renderToStaticMarkup } from "react-dom/server";
import { ArcWebViewer } from "./ui";

// Renders ui_2.tsx to a static HTML page, styled like the Swate metadata pages (light theme).
// Usage: npm run render -- <ro-crate.json> [query] [out.html]
const [cratePath, query = "", outPath = "ui_2.html"] = process.argv.slice(2);
if (!cratePath) throw new Error("Usage: npm run render -- <ro-crate.json> [query] [out.html]");

const body = renderToStaticMarkup(<ArcWebViewer jsonString={readFileSync(cratePath, "utf8")} query={query} />);

writeFileSync(outPath, `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>ARC Web Viewer</title>
<style>
:root { --primary: oklch(0.7305 0.13 177.47); --content: oklch(21% 0.006 285.885); }
body { margin: 0; padding: 2rem; background: oklch(98% 0 0); color: var(--content); font: 14px/1.5 system-ui, sans-serif; }
section {
  max-width: 30rem; padding: 1.5rem; background: #fff;
  border: 2px solid oklch(95% 0 0); border-radius: 0.5rem;
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
}
h2 { margin: 0; font-size: 1.875rem; color: var(--primary); }
dl { margin: 0; }
dt { padding-top: 1.5rem; margin-bottom: 0.5rem; font-weight: 600; color: var(--primary); }
dd + dt { margin-top: 0.5rem; border-top: 1px solid var(--content); }
dd {
  margin: 0; padding: 0.55rem 0.75rem; min-height: 1.5em;
  border: 1px solid color-mix(in oklab, var(--content) 20%, transparent); border-radius: 0.25rem;
}
</style>
</head>
<body>${body}</body>
</html>
`);
console.log(`Wrote ${outPath}`);
