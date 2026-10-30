
from arctrl import ARC, ArcRun, ArcTable, CompositeHeader, CompositeCell, IOType, OntologyAnnotation, Data

from pathlib import Path

DESEQ_DESIGN = "dds"
PROTOCOL_URI = "https://github.com/nfdi4plants/PyDESeq2"
def path_to_data(path: Path, arc_path: Path) -> Data:
    relative_path = path.relative_to(arc_path)
    return Data.init(
        name=relative_path.name,
        path=str(relative_path),
        format=path.suffix.lstrip("."),
    )



def build_preprocessing_table(
    name: str, inputs: list[Data], outputs: list[Data], design: str
) -> ArcTable:
    # Initialize table with name
    table = ArcTable.init(name=name)
    row_count = len(inputs) * len(outputs)
    # Add input column from file information
    table.AddColumn(
        header=CompositeHeader.input(IOType.data()),
        cells=[CompositeCell.data(source) for output in outputs for source in inputs],
    )
    # Add additional columns for protocol and software information
    table.AddColumn(
        header=CompositeHeader.protocol_uri(),
        cells=[CompositeCell.free_text(PROTOCOL_URI)] * row_count,
    )
    table.AddColumn(
        header=CompositeHeader.component(OntologyAnnotation.from_term_annotation(
            tan="http://purl.obolibrary.org/obo/NCIT_C150832", name="Software Name"
        )),
        cells=[CompositeCell.term(OntologyAnnotation(name="PyDESeq2"))] * row_count,
    )
    table.AddColumn(
        header=CompositeHeader.parameter(OntologyAnnotation(name="DESeq design pattern")),
        cells=[CompositeCell.term(OntologyAnnotation(name=design))] * row_count,
    )
    # Add output column from file information
    table.AddColumn(
        header=CompositeHeader.output(IOType.data()),
        cells=[CompositeCell.data(output) for output in outputs for source in inputs],
    )
    return table

def build_isa_tables(
    run: ArcRun,
    arc_path: Path,
    input_paths: list[Path],
    output_paths: dict[str, list[Path]],
    design: str = DESEQ_DESIGN,
) -> None:
    inputs = [path_to_data(path, arc_path) for path in input_paths]
    tables = []
    # for each output type, create a preprocessing table with the corresponding inputs and outputs
    for name, paths in output_paths.items():
        outputs = [path_to_data(path, arc_path) for path in dict.fromkeys(paths)]
        tables.append(build_preprocessing_table(name, inputs, outputs, design))
    for table in tables:
        run.SetTable(table.Name, table)