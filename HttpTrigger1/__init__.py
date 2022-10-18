import logging

import azure.functions as func
import requests
from validators import url
import json
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    #logging.info(req.get_json())
    # Require a token or identifier from the sending application to verify as a trusted source
    # Using a static token for tests / POC. A keyvault / secret manager would be better in prod
    private_auth_token = os.environ['private_auth_token']
    # CSPM sends a null payload to check the service is available, need to respond with a 200 status
    # to that
    try:
        if req.get_body().decode() == "":
          logging.info("Received a blank payload - probably a CSPM healthcheck. Sending 200 status")
          return func.HttpResponse(
             "OK",
             status_code=200
        )  
    except:
        logging.error("Could not process body as byte stream. Either blank or could not decode. Continuing...")
        pass


    # These are the minimum options required to forward a request
    required_args = ['destination', 'client_token', 'method']
       
    # Process body as JSON and fail if it's not
    try:
        req_body = req.get_json()
        onward_params = json.loads(req_body['remediationActions'][0].split(' ')[1])

    except ValueError as e:
        logging.error("Could not process body as JSON or could not find onward params in payload. Check remediation action is in the format cloudbot {[JSON parmas here]}")
        logging.error(e)
        return func.HttpResponse(
             "Unable to parse POST body as JSON. Please review the configuration of your application.",
             status_code=500
        )
    # Check to see if all of the required keys are present in the body once parsed

    if not all(k in onward_params.keys() for k in required_args):
        logging.error("Required values were not found in the body of the request.")
        logging.error(onward_params)
        return func.HttpResponse(
             "Required values were not found in the body. Please review the configuration of your application.",
             status_code=500
        )
    # Check the token provided matches

    if private_auth_token != onward_params['client_token']:
        logging.error("Auth token mismatch. Please verify and try again")
        return func.HttpResponse(
             "Invalid client token. Please verify and try again.",
             status_code=500
        )
    dest = onward_params['destination']
    payload = req_body
    h_method = onward_params['method']

    # Check the HTTP method provided is valid

    if not h_method.upper() in ['GET', 'POST']:
        logging.error("Could not find valid method in 'method' param. Needs to be GET/POST.")
        return func.HttpResponse(
             "HTTP method not in GET / POST. Please check and try again",
             status_code=500
        )
    
    # Check destination parameter is valid
    if url(dest) != True:
        logging.error("Invalid destination URL provided. Please check it includes the scheme and valid domain")
        return func.HttpResponse(
             "Destination URL is not valid. Please check and try again.",
             status_code=500
        )

    # Add headers if provided
    if  'headers' in onward_params:
        logging.info("Headers found in request - adding to payload")
        headers = onward_params['headers']
    else:
        headers = {}

    # All inputs good, build HTTP request

    if h_method.upper() == 'GET':
        logging.info(f"Sending GET request to {dest}")
        response = requests.get(dest)
    else:
        logging.info(f"Sending POST request to {dest}")
        response = requests.post(dest, json=payload, headers=headers)
    logging.info("Request sent to destination")
    logging.info(response.text)
    logging.info(response.status_code)
    return func.HttpResponse(
             response.text,
             status_code=response.status_code
        )


