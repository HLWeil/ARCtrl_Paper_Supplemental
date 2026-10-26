// Editor-only declarations for app code that is left out of the truncated ui.tsx snippet.
declare const jsonString: string;

declare function useMemoAsync<T>(
    factory: () => Promise<T>,
    deps: unknown[]
): T | undefined;

type SearchCache = { name: string; path: string; type: string };

declare const MetadataField: React.FC<{
    label: string;
    exists: boolean;
    children?: React.ReactNode;
}>;

declare const PersonsField: React.FC<{
    persons: import("@nfdi4plants/arctrl").Person[];
}>;
