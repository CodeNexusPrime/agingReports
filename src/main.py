import intune
import dell
import files
import pandas


def main ():
    app = intune.Create_Client_Application_Instance()
    
    token = intune.Create_Token(app=app)
    intune.Test_Token(token)
    
    access = intune.Create_Access(token_response=token)
    headers = intune.Create_Headers(access_token=access)
    
    devices = intune.Fetch_Devices(headers=headers)
    intune.Count_Devices(devices=devices)
    
    breakdownFile = files.Access_BreakDown_CSV("breakdowns.csv")
    files.Read_BreakDowns(breakdownFile)
    
        
        
    dataframe = intune.Convert_List_To_DataFrame(devices=devices)
    dataframe = intune.Filter_Devices(dataframe=dataframe, devicePrefixes=)

if __name__ == "__main__":
    main()