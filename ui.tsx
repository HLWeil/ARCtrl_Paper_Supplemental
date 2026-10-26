import { JsonController, ARC, ArcAssay, OntologyAnnotation } from "@nfdi4plants/arctrl";
import { Stack, Heading, Text } from "@primer/react";

/**

\subsection*{Arc Web Viewer (ts)}

The requirements for RDM tooling can be quite diverse. In this case, we wanted to create a minimal service for ARC exploration, which should be easily accessible and use a design pattern familiar to scientists working with the ARC. 

With the use of Primer's Product UI (https://primer.style/product/) we created a minimal web app and React (https://react.dev/) component library to upload an ARC RO-Crate JSON file (https://github.com/nfdi4plants/arc-wr-ro-crate-profile), read it into the ARCtrl datamodel, and develop search and visualization components based on it.

The following code snippets for each step are truncated for clarity.\\

\textbf{(1) - read the JSON file with ARCtrl}: The ARC JSON schema specification is complex and includes multiple sub-specifications (?), with the help of ARCtrl it is a single unified function call. 

 * UI components for the Arc Web Viewer
 */

const arc = useMemoAsync(async () => {
    return JsonController.ARC.fromROCrateJsonString(jsonString);    
}, [jsonString]);
/** 


\textbf{(2) Create unified search cache}: The user stories for finding information inside an ARC are diverse. Users might be interested in specific top level protocols, in the work of a specific person or even specific singular terms such as an organism. Therefore, we use ARCtrl to transform these diverse data into a unified search object.
*/


async function asyncDataToSearchCache(
    arc: ARC,
    setCache: React.Dispatch<React.SetStateAction<SearchCache[]>>
): Promise<void> {
    const headers = new Set<SearchCache>();
    // iterate over all assays in an ARC
    arc.Assays.forEach((assay) => {
        // replicate the internal file path, so we can navigate to the file if a user
        // selects a search result
        const path = `assays/${assay.Identifier}/isa.assay.xlsx`;
        // add assay title to search 
        headers.add({ name: assay.Identifier, path, type: "isa-title" });
        // add performers to search
        assay.Performers.forEach((contact) => {
            // add performer ORCID to search
            if (contact.ORCID) {
                headers.add({ name: contact.ORCID, path, type: "person" });
            }
            // add joined name of Performer to search
            const name = [
                contact.FirstName,
                contact.MidInitials,
                contact.LastName,
            ]
                .filter(Boolean)
                .join(" ");
            if (name) {
                headers.add({ name, path, type: "person" });
            }
        });
        // Iterate over workflows in assay
        assay.tables.forEach((table) => {
            // Add workflow name to search
            headers.add({ name: table.Name, path, type: "isa-table" });
            // Add workflow descriptors to search
            table.Headers.forEach((header) => {
                const term = header.TryGetTerm();
                if (term) {
                    const nametext = (term as OntologyAnnotation).NameText;
                    if (nametext) {
                        headers.add({ name: nametext, path, type: "header" });
                    }
                }
            });
        });
    });
    // Repeat this for studies, runs, workflows, investigation
    // ..
}
/** 

\textbf{(3) - Display ARC information to user}: ARC information is typically stored in different JSON types or in a isa.xlsx format. While isa.xlsx consists of human readable patterns, simply displaying a JSON file will introduce additional difficulty for searchability and understandability. To mitigate this problem, we will display the ARC information using simple tables, as well as labeled, read-only form fields. Accessing the ARC information can be done with ARCtrl.

*/
// ArcAssay is a type provided by ARCtrl
export default function AssayMetadata({ assay }: { assay: ArcAssay }) {
    return (
        <Stack spacing={2}>
            // Access information from ARCtrl data model
            <Heading as="h2">{assay.Identifier}</Heading>
            <MetadataField label="Title" exists={!!assay.Title}>
                <Text>{assay.Title}</Text>
            </MetadataField>
            <MetadataField label="Description" exists={!!assay.Description}>
                <Text>{assay.Description}</Text>
            </MetadataField>
            <MetadataField
                label="Measurement Type"
                exists={!!assay.MeasurementType}
            >
                <Text>{assay.MeasurementType?.NameText}</Text>
            </MetadataField>
            <MetadataField
                label="Technology Platform"
                exists={!!assay.TechnologyPlatform}
            >
                <Text>{assay.TechnologyPlatform?.NameText}</Text>
            </MetadataField>
            <MetadataField
                label="Technology Type"
                exists={!!assay.TechnologyType}
            >
                <Text>{assay.TechnologyType?.NameText}</Text>
            </MetadataField>

            <MetadataField
                label="Performers"
                exists={assay.Performers.length > 0}
            >
                // Composite component for objects from ARCtrl
                // Similiar implementation to this component
                <PersonsField persons={assay.Performers} />
            </MetadataField>
        </Stack>
    );
}
/**

Updating the app to new specification changes, can be done by updating ARCtrl. With a strict TypeScript parser, changes, introducing errors, can be caught and fixed.

For the full source code wrapped as a CLI tool, see section Software availability.
*/