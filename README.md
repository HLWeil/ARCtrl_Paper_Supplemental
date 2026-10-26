# ARCtrl Paper Snippets

Collection of example scripts to be used as use cases for the JIB ARCtrl paper.

## Local Installation

#### Requirements


- [nodejs and npm](https://nodejs.org/en/download)
    - verify with `node --version` (Tested with v24.22.1)
    - verify with `npm --version` (Tested with v11.19.1)
- [.NET SDK](https://dotnet.microsoft.com/en-us/download)
    - verify with `dotnet --version` (Tested with 10.0.401)
- [Python](https://www.python.org/downloads/) and [uv](https://pypi.org/project/uv/)
    - verify with `py --version` (Tested with 3.12.2, known to work only for >=3.11)
    - verify with `uv --version` (Tested with 0.13.5)

##### Windows

On windows you can use the `setup.cmd` to run the following steps automatically!

1. Setup dotnet tools

   `dotnet tool restore`


2. Install NPM dependencies

    `npm install`

3. Setup python environment

    - `py -m venv .venv`
    - `uv pip install -r pyproject.toml`

