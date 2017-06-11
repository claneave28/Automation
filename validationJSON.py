#!/usr/bin/env python2.7

# Carl Laneave
# Thermofisher Scientific
# Created 12/19
# A program using the jsonschema Python library.
# Uses it to validate some JSON data.
# Follows the Unix convention of writing normal output to the standard
# output (stdout), and errors to the standard error output (stderr).
# Need to find way to remove unicode 'u' in front of sys.stderr
# tee piping required to show on screen and text results

from __future__ import print_function
import sys
import json
import jsonschema
from jsonschema import validate
from mailer import Message
import smtplib
import subprocess
import logging

#Global Variables
jsonLocationUS='YOURJSONFILETOBETESTED'
jsonLocationEU = 'YOURJSONFILETOBETESTED'
JsonLocationCA = 'YOURJSONFILETOBETESTED'
jsonSchemaLocation='jsonSchema.json'
outputTxt='output.txt'

try:
    parameter = sys.argv[1]
except IndexError:
    parameter = "Missing parameter [REGION]"
    print(parameter)
    sys.exit(1)

totalRecordTxt= 'totalRecords'+parameter+'.txt'

def main(): 
    if parameter == "EU":
        jsonLocation = jsonLocationEU
    if parameter == "CA":
        jsonLocation = jsonLocationCA
    if parameter == "US":
        jsonLocation = jsonLocationUS
    verifyJson(jsonLocation)

#Function to find the exact line number in which the failed record error was found
def errLineLocation():
    #with open('fulljson.json') as jsonfile:
        #json1 = json.load(jsonfile)
        #jsonfile.close()
    shellScript = './getRow'+parameter+'.sh'
    results = subprocess.check_output([shellScript])
    test="Errors Found: \n**************\n\n" +results
    print(test)
    sys.stderr.write(str(test))
    #newemail(test)

#Creates email and sends list of errors to distributive list
def newemail(error):
    #Currently setup for gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("youremail", "YOURPASSWORD")
    fp = open(outputTxt)
    message = Message(From="SENDEREMAIL",
                      To="RECIEVEREMAIL",
                      charset="utf-8")
    message.Subject = 'Service Validation has FAILED!!!'
    message.Body ='\n' + error + '\n'.join(fp.readlines())
    #message.Body = 'Hello, \n\n  The validation job has FAILED for Web Service Validation!!!  Please refer to the error below for failed results\n'.join(fp.readlines())
    fp.close()
    server.sendmail("YOUREMAIL", "RECEIVERSEMAIL", message.as_string())
    server.quit()

#Validates the total record count vs the previous count.  Req:  Queries should INCREASE or stay the same from previous value
def totalRecordValidation(jsonLocation):
    recordtotal = 0
    jsonLocation1 = jsonLocation
    totalRecordTxt = "totalRecords"+parameter+".txt"
    with open(jsonLocation1) as json_schema:
        reader = json.load(json_schema)
        for row in reader:
            for item in row:
                if item == "query":
                    recordtotal += 1
    with open(totalRecordTxt, 'r') as myfile:
        data=myfile.read()
        data1=int(data)
        recordtotal1=int(recordtotal+(data1*.1))
        if data1 > recordtotal1:
            error="*************************\nFailure! Query totals are off!\n Current Record count #"+str(recordtotal)+" is less than previous record count of #"+str(data)+"\n**************************"
            sys.stderr.write(str(error))
            newemail(error)
            sys.exit(1)
            #10% variance allowance 
        elif data1 <= recordtotal1:
            print("Current record count is equal to or more than last query record count: True")
            writeRecordSuccess(recordtotal)

#Writes Total records based by Query when count is equal or higher from last run
def writeRecordSuccess(recordtotal):
    totalRecordTxt = "totalRecords"+parameter+".txt"
    with open(totalRecordTxt, 'w') as text_file:
        recordtotal1=str(recordtotal)
        text_file.write(recordtotal1)

#opens Schema file for validation
def verifyJson(jsonRegion):
    jsonLocation = jsonRegion
    with open(jsonSchemaLocation) as json_schema:
        schema = json.load(json_schema)
        # The data to be validated:
    with open(jsonLocation) as json_data:
        data = json.load(json_data)
    print("********Validating********\n")
    errorcount=0
    for idx, item in enumerate(data):
        try:
            validate(item, schema)
            sys.stdout.write("Record #{}: OK\n".format(idx))
        except jsonschema.exceptions.ValidationError as ve:
            sys.stderr.write(str("\nRecord #{}: ERROR\n".format(idx)))
            sys.stderr.write(str(ve)+ "\n************************* \n")
            errorcount+=1
    errorcount1=str(errorcount)
    if(errorcount>0):
        print("\n************************* \n")
        print("Total JSON Record Errors Found: "+errorcount1)
        errLineLocation()
        totalRecordValidation(jsonLocation)
        sys.exit(1) 
    elif(errorcount==0):
        totalRecordValidation()
        print("\n****No Errors Found: Testing Complete****")
        sys.exit(0)

main()


