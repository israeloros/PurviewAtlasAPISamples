import requests
import json
import os
import sys
import re
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.purview.catalog import PurviewCatalogClient
from pyapacheatlas.core import PurviewClient

# Define the colors for the output
green='\033[32m'
cyan='\033[36m'
yellow='\033[33m'
red='\033[31m'
reset='\033[0m'
pipe='\033[36m|\033[0m'
envFile = 'purview.env'

# Function to clear the screen
def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to wrap text to a specified width with optional padding
def strWrap(text, width, padding=0):
    for i in range(0, len(text), width):
        if i == 0:
            wrappedDescription = f"{text[i:width]}"
        else:
            if padding == 0:
                wrappedDescription = f"{wrappedDescription}\n{text[i:i+width]}"
            else:
                wrappedDescription = f"{wrappedDescription}\n{' '.rjust(padding)}{text[i:i+width]}"
    return wrappedDescription

# Function to refresh the credentials and get the access token
def refreshCredentials():
    # Get the access token using DefaultAzureCredential
    credential = DefaultAzureCredential()
    # Define the API endpoint for getting the access token
    accessToken = credential.get_token(f"https://purview.azure.net/.default").token
    # Set up the headers with the access token
    headers = { "Authorization": f"Bearer {accessToken}" }
    return credential,accessToken,headers

# Function to get the API response from the specified endpoint
def getAPIResponse(url, headers):
    try:
        # Send a GET request to the API endpoint
        response = requests.get(url, headers=headers)
        # Check if the request was successful
        if response.status_code == 200:
            responseJSON = response.json()
            return responseJSON 
        elif response.status_code == 404:
            print("Error 404: The requested resource could not be found. Please check the endpoint URL and Purview account name.")
            return None
        else:
            print(f"Failed to retrieve data sources. Status code: {response.status_code}")
            print(response.text)
            return None
    except:
        print(f"Failed to retrieve data sources. Please check the endpoint URL and try again.")
        return None
    
# Function to list all data sources for a Purview account
def listDataSources(endpoint, headers):
    # Define the API endpoint for listing data sources
    url = f"{endpoint}/scan/datasources?api-version=2023-09-01"
    # Send a GET request to the API endpoint
    response = getAPIResponse(url, headers)
    # Check if the request was successful
    if response:
        print("Registered Data Sources:")
        # Uncomment the line below to print the raw JSON response and inspect the structure
        # print(json.dumps(data_sources, indent=2))
        print(f"\n\n{green}{'Name':<30} {'Resource Type':<20} {'Resource Group':<20} {'Subscription Id':<36} {'Resource Name':<20} {'Region':<16}{reset}")
        for entity in response['value']:
            strProperties = ""
            if len(entity['properties']) > 0:
                if 'resourceGroup' in entity['properties']:
                    if entity['properties']['resourceGroup']:
                        strProperties += f"{entity['properties']['resourceGroup']:<21}"
                if 'subscriptionId' in entity['properties']:
                    if entity['properties']['subscriptionId']:
                        strProperties += f"{entity['properties']['subscriptionId']:<37}"
                if 'resourceName' in entity['properties']:
                    if entity['properties']['resourceName']:
                        strProperties += f"{entity['properties']['resourceName']:<21}"
                if 'location' in entity['properties']:
                    if entity['properties']['location']:
                        strProperties += f"{entity['properties']['location']:<17}"
            print(f"{entity['name']:<30} {entity['kind']:<20} {strProperties}")
        print(f"\n\n")

# Function to list all integration runtimes for a Purview account
def listIntegrationRuntimes(endpoint, headers):
    # Define the API endpoint for listing integration runtimes
    url = f"{endpoint}/scan/integrationruntimes?api-version=2023-09-01"
    # Send a GET request to the API endpoint
    response = getAPIResponse(url, headers)
    # Check if the request was successful
    if response:
        print(f"\n\n{green}Integration Runtimes:{reset}\n\n")
        # Uncomment the line below to print the raw JSON response and inspect the structure
        # print(json.dumps(response, indent=3))
        print(f"\n\n{green}{'Name':<40} {'Kind':<20} {'Properties':<40}{reset}")
        for entity in response['value']:
            if 'managedVirtualNetwork' in entity['properties']:
                print(f"{entity['name']:<40} {entity['kind']:<20} {strWrap(str(entity['properties']['managedVirtualNetwork']), 30, padding=62)}")
            else:
                print(f"{entity['name']:<40} {entity['kind']:<20}")
        print(f"\n\n")

# Function to list all typedefs
def listTypedefs(endpoint, headers):
    # Define the API endpoint for listing Type Definitions
    url = f"{endpoint}/catalog/api/atlas/v2/types/typedefs"
    response = getAPIResponse(url, headers)
    # Check if the request was successful
    if response:
        keyword = input(f"{red}Enter a typeDef pattern to find: {reset}")
        print(f"\n\nListing Type Definitions:\n\n")
        print(f"\n\n{green}{'Name':<80} {'Category':<20} {'Version':<20} {'Description':<30}{reset}")
        # Uncomment the line below to print the raw JSON response and inspect the structure to help you identify the attributes you need
        # print(f"{json.dumps(response,indent=3)}")
        for typedef in response.get("enumDefs", []) + response.get("structDefs", []) + response.get("classificationDefs", []) + response.get("entityDefs", []) + response.get("relationshipDefs", []):
            if 'description' in typedef:
                wrappedDescription = strWrap(typedef['description'], 30, 123)
            else:
                wrappedDescription = ""
            if re.search(keyword,typedef['name']):
                print(f"{typedef['name']:<80} {typedef['category']:<20} {typedef['version']:<20} {wrappedDescription}")

# Function to list assets with managed attributes only
def listManagedAttributes(endpoint,credential):
    clearScreen()
    print(f"\n\nListing assets with managed attributes... {yellow}It may take several minutes to complete.{reset}\n\n")
    try:
        purviewClient = PurviewCatalogClient(endpoint=endpoint, credential=credential)
        search_request = {
            # Keywords to search for
            "keywords": "*",
            "limit": 1000,
            # You can enhance the search by adding more filters
            "filter": {
                    # "and" : [
                    #     {"assetType": "Azure SQL Data Warehouse"},
                    "objectType": "Tables"
                    # ]
                }
        }
        # Run the search query
        response = purviewClient.discovery.query(search_request=search_request)
        # Loop through the results and print the asset name and related business attributes
        for asset in response['value']:
            entityResponse = purviewClient.entity.get_by_guid(asset['id'])
            if 'businessAttributes' in entityResponse['entity']:
                print(f"Asset Name: {asset['name']} - {asset['id']}")
                print(json.dumps(entityResponse['entity']['businessAttributes'],indent=3))
    except:
        print(f"Failed to list assets with managed attributes. Please check the endpoint URL and try again.")

# Function to query the map using a keyword to limit the search results
def queryMap(endpoint,credential,headers):
    clearScreen()
    keyword = input(f"{red}Enter the keyword to search for: {reset}")
    print(f"\n\nListing details for assets with assigned classifications... {yellow}It may take several minutes to complete.{reset}\n\n")
    try:
        purviewClient = PurviewCatalogClient(endpoint=endpoint, credential=credential)
        search_request = {
            # Keywords to search for
            "keywords": keyword,
            "limit": 1000
        }
        # Run the search query
        response = purviewClient.discovery.query(search_request=search_request)
        # Loop through the results and print the asset name and related business attributes
        for asset in response['value']:
            print(json.dumps(asset,indent=3))
            url = f"{endpoint}/datamap/api/atlas/v2/entity/guid/{asset['id']}"
            assetInfo = getAPIResponse(url, headers)
            print(json.dumps(assetInfo,indent=3))
            input("Press Enter to continue...")
    except:
        print(f"Failed to list assets details.")

# Function to list asset classifications details
def getClassifications(endpoint,credential,headers):
    clearScreen()
    print(f"\n\nListing details for assets with assigned classifications... {yellow}It may take several minutes to complete.{reset}\n\n")
    try:
        purviewClient = PurviewCatalogClient(endpoint=endpoint, credential=credential)
        search_request = {
            # Keywords to search for
            "keywords": "sales_transactions",
            "entityTypes": ["databricks_table"],
            "limit": 1000
        }
        # Run the search query
        response = purviewClient.discovery.query(search_request=search_request)
        # Loop through the results and print the asset name and related business attributes
        assetGuids = []
        for asset in response['value']:
                # Required only for testing purposes
                # if 'classification' in asset:
                #     if asset['id'] == '2e0a4219-06c0-4cc7-b798-19f6f6f60000':
                #     print(f"Asset Name: {asset['name']} - {asset['id']} - {asset['collectionId']} - {asset['displayText']} - {asset['classification']}")
                assetGuids.append([asset['id'],asset['name']])           
        print(f"{green}Listing asset details by GUID.{reset}")
        for assetGuid in assetGuids:
            url = f"{endpoint}/datamap/api/atlas/v2/entity/guid/{assetGuid[0]}"
            response = getAPIResponse(url, headers)
            classifications = ""
            for asset in response['referredEntities']:
                if 'classifications' in response['referredEntities'][asset]:
                    for classification in response['referredEntities'][asset]['classifications']:
                        # print(f"\t\t{red}{classification['typeName']}{reset}")
                        if classifications == "":
                            classifications = f"{classification['typeName']}"
                        else:
                            if re.search(classification['typeName'],classifications) == None:
                                classifications += f", {classification['typeName']}"
                    print(f"{assetGuid[1]} - {asset} - {response['referredEntities'][asset]['attributes']['name']} - {red}{classifications}{reset}")
    except:
        print(f"Failed to list assets details.")

# Function to define the menu options and dynamically assign credentials to each option
def menuContents(purviewEndpointUrl, headers, credential):
    return [
        (f"List Purview Data Sources", listDataSources, (purviewEndpointUrl, headers)),
        (f"List Integration Runtimes", listIntegrationRuntimes, (purviewEndpointUrl, headers)),
        (f"List Assets with Managed Attributes", listManagedAttributes, (purviewEndpointUrl, credential)),
        (f"List Typedefs", listTypedefs, (purviewEndpointUrl, headers)),
        (f"List Asset Classifications", getClassifications, (purviewEndpointUrl, credential, headers)),
        (f"Query Map", queryMap, (purviewEndpointUrl, credential, headers)),
        (f"Refresh Credentials", refreshCredentials, ()),
        (f"{red}Exit{reset}\n", None, (None, None))
    ]

# Function to display the menu
def showMenu(options):
    clearScreen()
    print(f"\n\n{green}{'Purview Inventory Tool':^60}{reset}\n")
    print(f"Option Menu:\n")
    for i, (description, _, _) in enumerate(options, 1):
        print(f"\t{i}. {description}")

# Function to get the user's choice from available menu options
def getChoice(num_options):
    while True:
        try:
            choice = int(input("Choose an option: "))
            if 1 <= choice <= num_options:
                return choice
            else:
                print(f"Please enter a number between 1 and {num_options}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# Main function
def main():
    # Read environment variables and assign to local variables or exit if the file is not found
    if os.path.exists(envFile):
        load_dotenv(envFile)       
        tenantId=os.getenv("TENANT_ID")
        clientId=os.getenv("CLIENT_ID")
        clientSecret=os.getenv("CLIENT_SECRET")
        subscriptionId=os.getenv("SUBSCRIPTION_ID")
        purviewAccountName=os.getenv("PURVIEW_ACCOUNT_NAME")
        # Define the API endpoint for listing data sources
        purviewEndpointUrl = f"https://{purviewAccountName}.purview.azure.com"
    else:
        clearScreen()
        print(f"\n\n{red}Failed to load environment variables from {yellow}{envFile}{red} file. Please check the file and try again.{reset}\n\n")
        sys.exit(0)

    # Get the access token using DefaultAzureCredential
    credential,accessToken,headers = refreshCredentials()

    # Define the menu options
    menuOptions = menuContents(purviewEndpointUrl, headers, credential)

    # Display the menu and get the user's choice
    while True:
        showMenu(menuOptions)
        choice = getChoice(len(menuOptions))
        if choice == len(menuOptions):
            print("Exiting...")
            break
        else:
            _, func, args = menuOptions[choice - 1]
            if _ == "Refresh Credentials":
                # Refresh the credentials, get the access token, and update menuOptions
                credential,accessToken,headers = func(*args)
                menuOptions = menuContents(purviewEndpointUrl, headers, credential)
                print(f"{green}Credentials refreshed successfully.{reset}")
                input("Press Enter to continue...")
            else:
                if func:
                    func(*args)
                    input("Press Enter to continue...")

# Call the main function
if __name__ == "__main__":
    main()