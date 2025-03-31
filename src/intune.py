from secretInformation import CLIENT_ID, CLIENT_SECRET, NONPROFIT_TENANT_ID, AUTHORITY, SCOPE
from logs import Logger
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

log_instance = Logger().get_logger()

def Create_Client_Application_Instance():
    app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
    )
    log_instance.debug("App created successfully.")
    return app

def Create_Token(app):
    token_response = app.acquire_token_for_client(scopes=SCOPE)
    log_instance.debug("Access Token Created.")
    return token_response

def Test_Token(token_response):
    if "access_token" not in token_response:
        log_instance.critical("Could not acquire token. Check your client credentials and permissions.")
        # print("Could not acquire token. Check your client credentials and permissions.")
        exit()
    log_instance.debug("Token worked during test.")

def Create_Access(token_response):
    access_token = token_response["access_token"]
    log_instance.debug("Access Token created successfully.")
    return access_token

def Create_Headers(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    log_instance.debug("Headers created successfully.")
    return headers

def Fetch_Devices(headers):
    devices = []
    endpoint = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices"
    log_instance.info("Fetching devices from Intune")
    # print("Fetching devices from Intune...")
    
    while endpoint:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            log_instance.debug("During Fetching devices reponse was 200.")
            data = response.json()
            devices.extend(data.get("value", []))
            # Check if there is a nextLink for pagination.
            log_instance.debug("Checking if there is a nextLink for pagination.")
            endpoint = data.get("@odata.nextLink")
        else:
            log_instance.error("Error fetching data:", response.status_code, response.text)
            # print("Error fetching data:", response.status_code, response.text)
            break
    
    return devices

def Count_Devices(devices):
    log_instance.info(f"Total devices retrieved: {len(devices)}")
    # print(f"Total devices retrieved: {len(devices)}")

def Convert_List_To_DataFrame(devices):
    dataframe = pandas.DataFrame(devices)
    log_instance.debug("Dataframe successfully created from the device list.")
    return dataframe

def Drop_Columns(dataframe, COLUMNS_TO_REMOVE=COLUMNS_TO_REMOVE):
    if COLUMNS_TO_REMOVE:
        log_instance.debug("Removing unneeded columns. In function intune.Drop_Columns().")
        dataframe= dataframe.drop(columns=COLUMNS_TO_REMOVE, errors="ignore")
    return dataframe

def Add_Department_Column(dataframe):
    dataframe["department"] = ""
    log_instance.debug("Adding the department column.")
    return dataframe

def Add_WarrantyInfo_Column(dataframe):
    dataframe["warrantyInfo"] = ""
    log_instance.debug("Adding the warrantyInfo column.")
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
        log_instance.info(f"Filtered to {len(dataframe_filtered)} Windows company devices.")
        # print(f"Filtered to {len(dataframe_filtered)} Windows company devices.")
    else:
        dataframe_filtered = dataframe
        log_instance.info("No 'operatingSystem' field found; using all devices.")
        # print("No 'operatingSystem' field found; using all devices.")
    
    if devicePrefixes:
        if "deviceName" in dataframe_filtered:
            # Use tuple() so we can pass multiple prefixes to startswith.
            dataframe_filtered = dataframe_filtered[dataframe_filtered['deviceName'].str.startswith(tuple(devicePrefixes), na=False)]
            log_instance.info(f"After filtering for device prefixes {devicePrefixes}, {len(dataframe_filtered)} devices remain.")
            # print(f"After filtering for device prefixes {devicePrefixes}, {len(dataframe_filtered)} devices remain.")
        else:
            log_instance.info("Column 'deviceName' not found; skipping device prefix filtering.")
            # print("Column 'deviceName' not found; skipping device prefix filtering.")
    
    if emailDomains:
        if "emailAddress" in dataframe_filtered.columns:
            # Use tuple() so we can pass multiple prefixes to startswith.
            dataframe_filtered = dataframe_filtered[dataframe_filtered['emailAddress'].str.endswith(tuple(emailDomains), na=False)]
            log_instance.info(f"After filtering for email domains {emailDomains}, {len(dataframe_filtered)} devices remain.")
            # print(f"After filtering for email domains {emailDomains}, {len(dataframe_filtered)} devices remain.")
        else:
            log_instance.info("Column 'emailAddress' not found; skipping email domain filtering.")
            # print("Column 'emailAddress' not found; skipping email domain filtering.")
    
    dataframe_filtered = Drop_Columns(dataframe=dataframe_filtered, COLUMNS_TO_REMOVE=COLUMNS_TO_REMOVE)
    dataframe_filtered = Add_Department_Column(dataframe=dataframe_filtered)
    dataframe_filtered = Add_WarrantyInfo_Column(dataframe=dataframe_filtered)
    
    return dataframe_filtered
    
def Export_Devices(dataframe,reportsDir, devicePrefixes=None, emailDomains=None):
    base_filename = os.path.join(reportsDir, "intune_computers")
    if devicePrefixes:
        prefixes = ''.join(devicePrefixes)
        prefixes = prefixes.split(' ')
        base_filename += "_" + "_".join(prefixes)
    if emailDomains:
        domains = ''.join(emailDomains)
        domains = domains.split(' ')
        base_filename += "_" + "_".join(domains)
    base_filename += ".xlsx"
    
    dataframe.to_excel(base_filename, index=False)
    log_instance.info(f"Excel file '{base_filename}' created successfully.")
    # print(f"Excel file '{base_filename}' created successfully.")

