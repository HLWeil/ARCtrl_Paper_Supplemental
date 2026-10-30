import { ARC, ArcAssay, Person } from "@nfdi4plants/arctrl";

/**
 * ARC Web Viewer: full version of the snippets used in the paper.
 * Render it to static HTML with `npm run render -- <ro-crate.json> [query]`.
 */

/** A name to search for, what kind of name it is, and the assay it belongs to. */
type SearchEntry = { name: string; type: string; assayId: string };

// Figure A: build a search index over all assays of an ARC
export function buildSearchIndex(arc: ARC): SearchEntry[] {
    const index: SearchEntry[] = [];
    for (const assay of arc.Assays) {
        const add = (name: string | undefined, type: string) => {
            if (name) index.push({ name, type, assayId: assay.Identifier });
        };
        add(assay.Identifier, "identifier");            // general assay metadata
        add(assay.Title, "title");
        for (const person of assay.Performers) {        // people, by ORCID and name
            add(person.ORCID, "person");
            add(fullName(person), "person");
        }
        for (const table of assay.Tables) {             // annotation tables
            add(table.Name, "table");
            for (const header of table.Headers) {       // e.g. Parameter [temperature]
                if (header.IsCvParamColumn) add(header.ToTerm().NameText, "term");
            }
        }
    }
    return index;
}

const fullName = (p: Person) => [p.FirstName, p.LastName].filter(Boolean).join(" ");

// Figure B: show assay metadata as labeled, read-only fields
export function AssayMetadata({ assay }: { assay: ArcAssay }) {
    return (
        <section>
            <h2>Assay Metadata</h2>
            <dl>
                <MetadataField label="Identifier"
                    value={assay.Identifier} />
                <MetadataField label="Title"
                    value={assay.Title} />
                <MetadataField label="Description"
                    value={assay.Description} />
                <MetadataField label="Measurement Type"
                    value={assay.MeasurementType?.NameText} />
                <MetadataField label="Technology Type"
                    value={assay.TechnologyType?.NameText} />
                <MetadataField label="Technology Platform"
                    value={assay.TechnologyPlatform?.NameText} />
                <MetadataField label="Performers"
                    value={assay.Performers.map(fullName).join(", ")} />
            </dl>
        </section>
    );
}

// One label and its value. The styling is in render_ui_2.tsx.
const MetadataField = ({ label, value }: { label: string; value?: string }) => (
    <><dt>{label}</dt><dd>{value}</dd></>
);

// Read the ARC and show the first assay matching the search query
export function ArcWebViewer({ jsonString, query }: { jsonString: string; query: string }) {
    const arc = ARC.fromROCrateJsonString(jsonString);
    const hit = buildSearchIndex(arc).find((e) => e.name.toLowerCase().includes(query.toLowerCase()));
    return hit ? <AssayMetadata assay={arc.GetAssay(hit.assayId)} /> : <p>No assay matches "{query}".</p>;
}
