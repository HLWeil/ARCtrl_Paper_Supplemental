from arctrl import ARC, Datamap, DataContext

'''
\subsection*{Validation of tabular data contained in \acp{ARC} (python)}

One of the advantages of having first-class ARC support in multiple programming languages is that it gives access to the respective package ecosystems.

frictionless \cite{karevFrictionlessPythonLibrary2025} is a python package used to describe, extract, validate, and transform tabular data. While validation of the metadata contained in an \ac{ARC} can be done on the ARCtrl data model in any of the supported programming language, validation of data files [brauch man halt extratools].

In this use case, ARCtrl is used to \textbf{(1)} extract data maps - a file that is used in an ARC to describe the content or fragments of a data file with metadata - from an ARC, \textbf{(2)} generate a frictionless schema for the file based on those descriptors, and \textbf{(3)} subsequently using frictionless to validate the file with the generated schema. The following code snippets for each step are truncated for clarity.\\

\textbf{(1) - aggregating datamaps in an ARC}: The following function extracts all data maps from an ARC (Assays, Studies, Workflows, and Runs can contain datamaps).

'''


# aggregate data maps from all objects in the data model that can contain one.
def aggregate_datamaps(arc: ARC) -> list[Datamap]:
    datamaps : list[Datamap] = []
    for assay in arc.Assays:
        if assay.DataMap is not None:
            datamaps.append(assay.DataMap)
    # ... repeat for studies, runs, and workflows accordingly
    return datamaps
'''

\textbf{(2) - generating and patching the frictionless schema}: frictionless can infer a schema based on actual values in the file via the \emph{describe} function, a process that heavily relies on the sampled entries. Since datamaps can contain typing information about the files they describe, their annotations can be used to improve this schema:

'''
def generate_frictionless_schema(
    basepath: str, 
    datacontext: DataContext
) -> frictionless.Metadata:
    #create schema from file
    fschema = frictionless.describe(datacontext.FilePath, basepath=basepath)
    # fieldName and column index are to be extracted from the fragment selector.
    # access all fragment selectors, patch schema accordingly
    for datacontext in datacontext.DataContexts:
        # fragment selector format for text/csv
        if datacontext.SelectorFormat == "https://datatracker.ietf.org/doc/html/rfc7111":
            if datacontext.GetValue().IsAnInt:
                # set the expected field type as indicated in the datamap
                fschema.schema.fields[column] = frictionless.fields.IntegerField(name=fieldName))
            # ... repeat for other types e.g. DateTime, Strings etc.                
    return fschema
'''

\textbf{(3) - validating the data files with frictionless}: The functions above can then be used to create a schema for each file described in a datamap and validate it based on the generated schema:

'''

def validate_datamaps(
    basepath:str, 
    arc: ARC
) -> TestSuite:
    # load arc from disk
    arc : arctrl.ARC = ARC.load(args.arc_path)
    data_maps = aggregate_datamaps(arc)
    for datamap in data_maps:
        for datacontext in datamap.DataContexts:
            schema = generate_frictionless_schema(basepath, datacontext)
            # validate data against the generated schema
            schema.validate()

'''

For the full source code wrapped as a CLI tool, see section Software availability. 
'''