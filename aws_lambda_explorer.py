'''
Useful for exploring lambda functions in different regions for those using Windows OS.
The application is build using PySimpleGUI. 
It expects you have setup the aws id/key in
Linux:   /home/[username]/.aws
Windows: /Users/[username]/.aws

To do:
1:
'''

import PySimpleGUI as sg
import boto3
from botocore.config import Config
from boto3.session import Session
import threading
import time
#import datetime
from datetime import datetime,timedelta
import sys

session = boto3.session.Session()

lambda_func_list_data=[]
lambda_func_data=[]

sg.theme('Reddit')

#-----------------GUI Layout--------------------------------    

Console =[
    [sg.Text("Console")],
    [sg.Multiline(size=(60, 14),key="-CONSOLEMSG-",disabled=True)],
    [sg.B("Clear Console",size=(27, 1)),sg.B("Save Console",size=(25, 1))]
    ]

frame_layout = [
                  [sg.T('FunctionName:'), sg.Text("",size=(60, 1),key="-text_funcname-")],
                  [sg.T('Description:'), sg.Text("",size=(60, 1),key="-text_desc-")],
                  [sg.T('CodeSha256:'), sg.Text("",size=(60, 1),key="-text_codesha-")],
                  [sg.T('Mode:'), sg.Text("",size=(46, 1),key="-text_mode-"),sg.T(' Runtime:'), sg.Text("",size=(13, 1),key="-text_runtime-")],
                  [sg.T('CodeSize (B):'), sg.Text("",size=(41, 1),key="-text_codesize-"),sg.T('MemorySize (MB):'), sg.Text("",size=(13, 1),key="-text_memorysize-")],
                  [sg.T('LastModified:'), sg.Text("",size=(41, 1),key="-text_lastmodifiedtime-"),sg.T(' Timeout (Sec):'), sg.Text("",size=(13, 1),key="-text_timeout-")],
                  [sg.T('State:'), sg.Text("",size=(47, 1),key="-text_state-"),sg.T('LastUpdateStatus:'), sg.Text("",size=(13, 1),key="-text_updatestatus-")],
                  [sg.T('Storage (MB):'), sg.Text("",size=(41, 1),key="-text_storage-"),sg.T('RepositoryType:'), sg.Text("",size=(13, 1),key="-text_repotype-")],
                  [sg.T('RevisionId:'), sg.Text("",size=(43, 1),key="-text_revid-"),sg.T(' Architecture:'), sg.Text("",size=(13, 1),key="-text_arch-")]
                  ]                                

Desc =[
        [sg.Frame('Description', frame_layout, font='Any 12', title_color='blue')]
        ]

cost_expl=[]


funct_list =[
     [sg.Table(values=lambda_func_list_data,key="_list_", headings=['Function Name', 'Package Type','Runtime','Last modified'],auto_size_columns=False, col_widths=[50, 10, 10,27],  num_rows=15,justification='left',enable_events=True )]
    ]

Region = [
         [sg.Text("Region Name (Select Region)")],
         [sg.Listbox(values=[],enable_events=True,size=(32, 12), key="-REGION-")], 
         [sg.B("List Regions",size=(30, 1))]
    ]
lambda_layout = [
    [
      sg.Column(Region,size=(255, 270)), sg.Column(funct_list)],      
      [sg.TabGroup(
         [[sg.Tab('Function Detail', Desc)],
          [sg.Tab('Cost Explorer', cost_expl)]])
      # sg.Column(Desc,size=(700, 270))
        ,sg.VSeperator(),
        sg.Column(Console)
      ]   
]


config =[
    [sg.Text('Enter Your AWS Id',size=(30, 1)), sg.InputText(key="-AWSID-",size=(30, 1))],
    [sg.Text('Enter Your AWS Key',size=(30, 1)), sg.InputText(key="-AWSKEY-",size=(30, 1))],
    [sg.Text('Enter Your Default Region',size=(30, 1)), sg.InputText(key="-DEFREGION-",size=(30, 1))],
    [sg.B("Reset",size=(28, 1)),sg.B("Connect",size=(27, 1))]
    ]


config_layout = [[sg.Column(config)]]

tabgrp = [[sg.TabGroup([[sg.Tab('Config', config_layout)],[sg.Tab('Lambda', lambda_layout)]])]]  



        
#---------- Lambda functions----------------------  
def lambda_function_worker_thread(region_name, window):
    try:
        data=[] 
        data = get_lambda_function_list(region_name,window)
        window["_list_"].update(data)                
    except Exception as e:
        window.write_event_value('-WRITE-',e)
        

def lambda_detail_worker_thread(region_name, function_name, window):
    try:
        describe_lambda_functions(region_name, function_name, window)                
    except Exception as e:
        window.write_event_value('-WRITE-',e)
        
def get_lambda_function_list(REGION_NAME,window):
    
    REGION_CONFIG = Config(
    region_name = REGION_NAME,
    signature_version = 'v4',
    retries = {
        'max_attempts': 3
        }
    )
        
    try:
        CLIENT = session.client('lambda', config=REGION_CONFIG)
        response = CLIENT.list_functions()
        lambda_func_list_data.clear()
        
        if not 'Functions' in response or len(response['Functions']) == 0:
            set_lambda_detail(window)
            window.write_event_value('-WRITE-',"There is no lambda function in this region")
        
        else:
            for function in response['Functions']:
                lambda_func_list_data.append([function['FunctionName'], 
                                  function['PackageType'], 
                                  function['Runtime'],
                                  function['LastModified']])
        
        return lambda_func_list_data
        
    except Exception as e:
        window.write_event_value('-WRITE-',e)


#get all the AWS regions
def get_lambda_regions():
    lambda_region = session.get_available_regions('lambda')
    return (lambda_region)



def set_lambda_detail(window):
    try:
        window["-text_funcname-"].update("")
        window["-text_runtime-"].update("")
        window["-text_codesize-"].update("")
        window["-text_memorysize-"].update("")
        window["-text_lastmodifiedtime-"].update("")
        window["-text_timeout-"].update("")
        window["-text_state-"].update("")
        window["-text_updatestatus-"].update("")
        window["-text_arch-"].update("")
        window["-text_repotype-"].update("")
        window["-text_desc-"].update("")
        window["-text_mode-"].update("")
        window["-text_codesha-"].update("")
        window["-text_revid-"].update("")
        window["-text_storage-"].update("")
    except Exception as e:
        window.write_event_value('-WRITE-',e)
    
    

def describe_lambda_functions(REGION_NAME, function_name, window):
    REGION_CONFIG = Config(
    region_name = REGION_NAME,
    signature_version = 'v4',
    retries = {
        'max_attempts': 3
        }
    )
        
    try:
        CLIENT = session.client('lambda', config=REGION_CONFIG)
        response = CLIENT.get_function(FunctionName=function_name)
        lambda_func_data.append([response['Configuration']['FunctionName'],
                                response['Configuration']['Runtime'],
                                response['Configuration']['CodeSize'],
                                response['Configuration']['Description'],
                                response['Configuration']['Timeout'],
                                response['Configuration']['MemorySize'],
                                response['Configuration']['LastModified'],
                                response['Configuration']['CodeSha256'],
                                response['Configuration']['TracingConfig']['Mode'],
                                response['Configuration']['State'],
                                response['Configuration']['LastUpdateStatus'],
                                #response['Configuration']['PackageType'],
                                response['Configuration']['RevisionId'],
                                response['Code']['RepositoryType'],
                                response['Configuration']['Architectures'],
                                response['Configuration']['EphemeralStorage']['Size']
                                ]                                
            )
    
    
        window["-text_funcname-"].update(response['Configuration']['FunctionName'])
        window["-text_runtime-"].update(response['Configuration']['Runtime'])
        window["-text_codesize-"].update(response['Configuration']['CodeSize'])
        window["-text_memorysize-"].update(response['Configuration']['MemorySize'])
        window["-text_lastmodifiedtime-"].update(response['Configuration']['LastModified'])
        window["-text_timeout-"].update(response['Configuration']['Timeout'])
        window["-text_state-"].update(response['Configuration']['State'])
        window["-text_updatestatus-"].update(response['Configuration']['LastUpdateStatus'])
        #window["-text_packagetype-"].update(response['Configuration']['PackageType'])
        window["-text_repotype-"].update(response['Code']['RepositoryType'])
        window["-text_desc-"].update(response['Configuration']['Description'])
        window["-text_mode-"].update(response['Configuration']['TracingConfig']['Mode'])
        window["-text_codesha-"].update(response['Configuration']['CodeSha256'])
        window["-text_revid-"].update(response['Configuration']['RevisionId'])
        window["-text_arch-"].update(response['Configuration']['Architectures'])
        window["-text_storage-"].update(response['Configuration']['EphemeralStorage']['Size'])
        
        
    except Exception as e:
        window.write_event_value('-WRITE-',e)




#-----------------Main function------------------------------------
def main():
    
    window = sg.Window('AWS Lambda Explorer', tabgrp) #layout
    
    region_loop = False
    
    while True: # The Event Loop
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        #---------Connection Tab-----------------------------
        if event == 'Reset':
            try:
                window["-AWSID-"].update("")
                window["-AWSKEY-"].update("")
                window["-DEFREGION-"].update("")
                window["-AWSID-"].SetFocus(force = True)
            except Exception as e:
                sg.popup(e)
        
        if event == 'Connect':
            try:
                global session
                
                if values['-DEFREGION-'] == "":
                    sg.popup("Region Field is missing")
                elif values['-AWSID-'] == "":
                    sg.popup("AWS ID Field is missing")
                elif values['-AWSKEY-'] == "":
                    sg.popup("AWS KEY Field is missing")
                else:
                    session = Session(region_name=values['-DEFREGION-'], aws_access_key_id=values['-AWSID-'],
                                  aws_secret_access_key=values['-AWSKEY-'])
                    #need to validate if connection is successful or not
                    sg.popup("Connection Established")
            except Exception as e:
                sg.popup(e)
                
                
        #--------------Lambda Tab-------------------------
        if event == 'List Regions':
            try:
                if region_loop == False: #don't refresh list everytime
                    region_list = get_lambda_regions()
                    window["-REGION-"].update(region_list)
                    region_loop = True
            except Exception as e:
                window["-CONSOLEMSG-"].update(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +": "+str(e)+"\n", append=True )

        

        if event == '-REGION-':
            try:

                    threading.Thread(target=lambda_function_worker_thread,
                                      args=(values['-REGION-'][0],
                                            window,),  daemon=True).start()
            except Exception as e:
                window["-CONSOLEMSG-"].update(str(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")) + ": "+str(e)+"\n", append=True)
                     
              
        if event == '-WRITE-':
            window["-CONSOLEMSG-"].update(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +": "+str(values['-WRITE-'])+"\n", append=True)
        
            
        if event == "_list_":
            try:
                data_selected = [lambda_func_list_data[row] for row in values[event]]               
                threading.Thread(target=lambda_detail_worker_thread, 
                                 args=(values['-REGION-'][0],data_selected[0][0],window,),  
                                 daemon=True).start()
                
            except Exception as e:
                  window["-CONSOLEMSG-"].update(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) +": "+str(e)+"\n", append=True )
  
    
                
        if event == 'Save Console':
            try:
                file= open(".\output.txt", 'a+')
            except FileNotFoundError:
                file= open(".\output.txt", 'w+')
            file.write(str(window["-CONSOLEMSG-"].get()))
            file.close()
            sg.popup("File Saved")
        
        
        if event == 'Clear Console':
            window["-CONSOLEMSG-"].update("")
    window.close()


if __name__ == '__main__':
    main()