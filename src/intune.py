from secretInformation import CLIENT_ID, CLIENT_SECRET, NONPROFIT_TENANT_ID, AUTHORITY, SCOPE
import msal
import requests
import pandas
import os

# Specify columns to remove if needed. For example:
COLUMNS_TO_REMOVE = [
    "id",
    "userId",
    "managedDeviceOwnerType",
    "complianceState",
    "jailBroken",
    "managementAgent",
    "easActivated",
    "easDeviceId",
    "easActivationDateTime",
    "azureADRegistered",
    "deviceEnrollmentType",
    "activationLockBypassCode",
    "deviceRegistrationState",
    "deviceCategoryDisplayName",
    "isSupervised",
    "exchangeLastSuccessfulSyncDateTime",
    "exchangeAccessState",
    "exchangeAccessStateReason",
    "remoteAssistanceSessionUrl",
    "remoteAssistanceSessionErrorDetails",
    "isEncrypted",
    "imei",
    "complianceGracePeriodExpirationDateTime",
    "phoneNumber",
    "androidSecurityPatchLevel",
    "configurationManagerClientEnabledFeatures",
    "wiFiMacAddress",
    "deviceHealthAttestationState",
    "subscriberCarrier",
    "meid",
    "totalStorageSpaceInBytes",
    "freeStorageSpaceInBytes",
    "managedDeviceName",
    "partnerReportedThreatState",
    "requireUserEnrollmentApproval",
    "managementCertificateExpirationDate",
    "iccid",
    "udid",
    "notes",
    "ethernetMacAddress",
    "physicalMemoryInBytes",
    "enrollmentProfileName",
    "deviceActionResults"
    ]  # Update with actual column names you wish to remove.


def Create_Client_Application_Instance():
    app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
    )
    return app

def Create_Token(app):
    token_response = app.acquire_token_for_client(scopes=SCOPE)
    return token_response

def Test_Token(token_response):
    if "access_token" not in token_response:
        print("Could not acquire token. Check your client credentials and permissions.")
        exit()

def Create_Access(token_response):
    access_token = token_response["access_token"]
    return access_token

def Create_Headers(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    return headers

def Fetch_Devices(headers):
    devices = []
    endpoint = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices"
    print("Fetching devices from Intune...")
    
    while endpoint:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            data = response.json()
            devices.extend(data.get("value", []))
            # Check if there is a nextLink for pagination.
            endpoint = data.get("@odata.nextLink")
        else:
            print("Error fetching data:", response.status_code, response.text)
            break
    
    return devices

def Count_Devices(devices):
    print(f"Total devices retrieved: {len(devices)}")

def Convert_List_To_DataFrame(devices):
    dataframe = pandas.DataFrame(devices)
    return dataframe

def Drop_Columns(dataframe, COLUMNS_TO_REMOVE=COLUMNS_TO_REMOVE):
    if COLUMNS_TO_REMOVE:
        dataframe= dataframe.drop(columns=COLUMNS_TO_REMOVE, errors="ignore")
    return dataframe

def Add_Department_Column(dataframe):
    dataframe["department"] = ""
    return dataframe

def Add_WarrantyInfo_Column(dataframe):
    dataframe["warrantyInfo"] = ""
    return dataframe
    

def Filter_Devices(dataframe, devicePrefixes=None, emailDomains=None, COLUMNS_TO_REMOVE=COLUMNS_TO_REMOVE, serialColumn="serialNumber"):
    """
    Filters the DataFrame of devices based on operating system and managed device owner type,
    optionally filters by device name prefixes and email address domains,
    cleans unwanted columns, adds warranty information,
    and then exports the filtered DataFrame to an Excel file with a name that reflects the filters.

    Parameters:
        df (pd.DataFrame): The DataFrame containing device data.
        device_prefixes (list, optional): List of prefixes for filtering the device names.
        email_domains (list, optional): List of email domains for filtering email addresses.
        columns_to_remove (list, optional): List of columns to remove from the DataFrame.
        serial_column (str): Name of the column containing the serial number.
        
    Returns:
        pd.DataFrame: The filtered and updated DataFrame.
    """
    if "operatingSystem" in dataframe.columns:
        dataframe_filtered = dataframe[dataframe['operatingSystem'].str.contains("Windows", case=False, na=False)]
        if "managedDeviceOwnerType" in dataframe.columns:
            dataframe_filtered = dataframe_filtered[dataframe_filtered['managedDeviceOwnerType'].str.contains("company", case=False, na=False)]
        print(f"Filtered to {len(dataframe_filtered)} Windows company devices.")
    else:
        dataframe_filtered = dataframe
        print("No 'operatingSystem' field found; using all devices.")
    
    if devicePrefixes:
        if "deviceName" in dataframe_filtered:
            # Use tuple() so we can pass multiple prefixes to startswith.
            dataframe_filtered = dataframe_filtered[dataframe_filtered['deviceName'].str.startswith(tuple(devicePrefixes), na=False)]
            print(f"After filtering for device prefixes {devicePrefixes}, {len(dataframe_filtered)} devices remain.")
        else:
            print("Column 'deviceName' not found; skipping device prefix filtering.")
    
    if emailDomains:
        if "emailAddress" in dataframe_filtered.columns:
            # Use tuple() so we can pass multiple prefixes to startswith.
            dataframe_filtered = dataframe_filtered[dataframe_filtered['emailAddress'].str.endswith(tuple(emailDomains), na=False)]
            print(f"After filtering for email domains {emailDomains}, {len(dataframe_filtered)} devices remain.")
        else:
            print("Column 'emailAddress' not found; skipping email domain filtering.")
    
    dataframe_filtered = Drop_Columns(dataframe=dataframe_filtered, COLUMNS_TO_REMOVE=COLUMNS_TO_REMOVE)
    dataframe_filtered = Add_Department_Column(dataframe=dataframe_filtered)
    dataframe_filtered = Add_WarrantyInfo_Column(dataframe=dataframe_filtered)
    
    return dataframe_filtered
    
def Export_Devices(dataframe,reportsDir, devicePrefixes=None, emailDomains=None):
    base_filename = os.path.join(reportsDir, "intune_computers")
    if devicePrefixes:
        base_filename += "_" + "_".join(devicePrefixes)
    if emailDomains:
        base_filename += "_" + "_".join(emailDomains)
    base_filename += ".xlsx"
    
    dataframe.to_excel(base_filename, index=False)
    print(f"Excel file '{base_filename}' created successfully.")

