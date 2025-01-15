# Purview Atlas API Samples Tool

This is a simple Python-based tool I created as a way to demonstrate how to interact with Microsoft Purview. It allows you to list data sources, integration runtimes, assets with managed attributes, typedefs, asset classifications at the column level, and query the map using a keyword. It provides some sample functionality that you can extend and adapt to your specific requirements. The script is provided for learning purposes and can be hardened based on your security standards.

## Prerequisites

- Python 3.6 or higher
- Python modules: requests, python-dotenv, azure-identity, azure-purview-catalog, and pyapacheatlas
- Microsoft Purview provisioned
- Azure login or Service Principal with the following privileges in Microsoft Purview:
  - Purview Data Reader
  - Purview Data Curator
  - These roles need to be granted in the root collection in Purview.
  - For additional information, please refer to the following Microsoft document. https://learn.microsoft.com/en-us/purview/tutorial-using-rest-apis


## Installation

1. Clone this repository or download the script and purview-sample.env.
2. Install the required Python packages using pip:
   ```bash
   pip install requests python-dotenv azure-identity azure-purview-catalog pyapacheatlas
3. Copy the contents of the purview-sample.env file or rename it to purview.env in the same directory where the PurviewAtlasAPISamples.py script will be located.

## Configuration

1. Update the values for the PURVIEW_ACCOUNT_NAME variable inside of the purview.env file. This is the only required variable.
2. If you don't want to use the Service Principal authentication method, please login into Azure using your credentials using the Azure CLI. 

## Available functionality

- List Purview Data Sources: Lists all data sources registered in the Purview account.
- List Integration Runtimes: Lists all integration runtimes for the Purview account.
- List Assets with Managed Attributes: Lists all assets with managed attributes.
- List Typedefs: Lists all type definitions.
- List Asset Classifications: Lists all asset classifications.
- Query Map: Queries the map using a keyword.
- Refresh Credentials: Refreshes the credentials.

## Usage

1.  Run the PurviewAtlasAPISamples.py as follows:
   ```bash
   python3 PurviewAtlasAPISamples.py
2. Follow the on-screen menu to interact with the Purview Inventory Tool.

## License
This project is licensed under the MIT License.
