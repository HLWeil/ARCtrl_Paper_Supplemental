(**


*)

#r "nuget: ARCtrl, 3.2.0"

open ARCtrl.ROCrate
open ARCtrl.Conversion
open ARCtrl
open ARCtrl.Json.ARC
open ARCtrl.Json
open System.IO

type GitLfsFile = { 
    name: string
    size: int64
    checkout: bool
    downloaded: bool
    oidType: string
    oid: string
    version: string 
}

type GitLfsFiles = {
    files: GitLfsFile []
}

let ro_crate_metadata_filename = ""

module GitLFS =

    let tryCreateGitLfsJson (repoDir: string) : GitLfsFiles option =
        failwith "Not implemented"

    let tryGetPathFromGitLfsJson (filePath: string) (arr: GitLfsFile []) : GitLfsFile option =
        failwith "Not implemented"

    let normalizePathToGitPath (path: string) =
        path.Replace("\\", "/").TrimStart('/')


let projectID = Some "https://github.com/HLWeil/ARCtrl_Paper_Snippets"
let gitlfsInfo = GitLFS.tryCreateGitLfsJson ""



// Define the schema.org property IRIs to be added
let sha256 = "http://schema.org/sha256"
let contentSize = "http://schema.org/contentSize"
let mainEntityOfPage = "http://schema.org/mainEntityOfPage"


// This function checks whether a generic node is a proper file, and not double typed as dataset
let isProperFileNode (n: LDNode) (context : LDContext option) =
    let nodeIsFile = LDFile.validate(n, ?context = context)
    let nodeIdIsPath = not (n.Id.Contains("#"))
    let nodeIsNotDataset = not (n.HasType(LDDataset.schemaType, ?context = context))
    nodeIsFile && nodeIdIsPath && nodeIsNotDataset

// This function updates a file node with the sha256 and contentSize properties from the Git LFS info
let updateFileNode (n: LDNode) (context : LDContext option) (lfsInfo : GitLfsFiles) =
    match GitLFS.tryGetPathFromGitLfsJson n.Id lfsInfo.files with
    | Some lfsFileInfo ->
        // For each file node, add the sha256 and contentSize properties from the Git LFS info
        match lfsFileInfo.oidType with
        | "sha256" ->
            n.SetProperty(sha256, lfsFileInfo.oid, ?context =context)
        | _ -> 
            ()
        n.SetProperty(contentSize, $"{lfsFileInfo.size}b", ?context = context)
    | None -> 
        ()

let create_ro_crate_metadata_LFSHashes (repoDir: string) (arc: ARC) =
    ()
    // Convert the ISA ARC Workspace model to an ARC RO-Crate Investigation
    let isa = arc.ToROCrateInvestigation(fs = arc.FileSystem, ignoreBrokenWR = true)
    // Set additional properties on the top-level
    LDDataset.setSDDatePublishedAsDateTime(isa, System.DateTime.Now)
    if projectID.IsSome then isa.SetProperty(mainEntityOfPage, projectID.Value)
    // Flatten the Investigation into a RO-Crate Graph 
    let graph = isa.Flatten()
    // Add the additional schema.org properties to the RO-Crate Graph context
    let customContextPart = Context.initBioschemasContext()
    customContextPart.AddMapping("sha256", sha256)
    let context = LDContext(baseContexts=ResizeArray[Context.initV1_1();customContextPart])
    graph.SetContext(context)
    ()

    let gitlfsInfo = GitLFS.tryCreateGitLfsJson repoDir
    match gitlfsInfo with
    | Some info when Array.isEmpty info.files ->
        ()
    | Some info ->
        // Iterate over all nodes
        graph.Nodes
        |> Seq.iteri (fun i n -> 
            if isProperFileNode n (Some context) then
                updateFileNode n (Some context) info
            )
    | None ->
        ()
    graph.Compact_InPlace()
    graph.ToROCrateJsonString(2)


let write_ro_crate_metadata_LFSHashes (repoDir: string) (outDir: string) (arc: ARC) =
    let path = Path.Combine(outDir, ro_crate_metadata_filename)
    printfn "Writing ARC RO-Crate metadata with LFS hashes to %s" path
    File.WriteAllText(path, create_ro_crate_metadata_LFSHashes repoDir arc)