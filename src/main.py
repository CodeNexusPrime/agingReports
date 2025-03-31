#!/usr/bin/env python3
import intune
import dell
import files
from logs import Logger


def main ():
    log_instance = Logger().get_logger()
    print(type(log_instance))
    log_instance.info("Starting the program")
    
    log_instance.info("Creating my application instance using intune.Create_Client_Application_Instance")
    app = intune.Create_Client_Application_Instance()
    
    log_instance.info(f"Creating my application instance using intune.Create_Token({app})")
    token = intune.Create_Token(app=app)
    
    log_instance.info(f"Testing the token using intune.Test_Token({token})")
    intune.Test_Token(token)
    
    log_instance.info(f"Creating my access from the token using intune.Create_Access({token})")
    access = intune.Create_Access(token_response=token)
    
    log_instance.info(f"Creating my headers from the token using intune.Create_Headers({access})")
    headers = intune.Create_Headers(access_token=access)
    
    log_instance.info(f"Fetching all devices from intune using intune.Fetch_Device({headers})")
    devices = intune.Fetch_Devices(headers=headers)
    intune.Count_Devices(devices=devices)
    
    log_instance.info(f"Creating a dataframe using panda that includes all devices pulled using the intune.Convert_List_To_DataFrame()")
    dataframe = intune.Convert_List_To_DataFrame(devices=devices)
    
    log_instance.info(f"Creating the breakdown reports for reporting needs. Using files.Access_Breakdown_CSV()")
    breakdownFile = files.Access_BreakDown_CSV("breakdowns.csv")
    files.Read_BreakDowns(breakdownFile, dataframe)
    

if __name__ == "__main__":
    main()