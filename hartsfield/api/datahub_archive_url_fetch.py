"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""
import datetime
import json
import re

from flask import current_app as app, request
from google.cloud import storage
from google.oauth2 import service_account
from hartsfield.api.auth_helper import authorzied_user_required
from hartsfield.lib.http import tolerant_jsonify
import hartsfield.api.read_aws_secret

PUBLIC_CONFIGS = [
    'DEV_AUTH_ENABLED',
    'HARTSFIELD_ENV',
    'TIMEZONE',
]

AWS_SECRETS_NAME_GCP_JSON_CREDENTIALS = app.config['AWS_SECRETS_NAME_GCP_JSON_CREDENTIALS']


gcp_json_credentials_from_aws = hartsfield.api.read_aws_secret.read_aws_secret(AWS_SECRETS_NAME_GCP_JSON_CREDENTIALS)
gcp_json_credentials_dict = json.loads(gcp_json_credentials_from_aws)


@app.route('/api/fetch_url_direct', methods=['POST'])
@authorzied_user_required
def fetch_url_direct():

    params = request.get_json()
    gs_source_url = params.get('gsSourceUrl')
    gs_source_url = gs_source_url.strip()
    if not re.match(r'gs://.{3,}/.+', gs_source_url):
        error_message = 'The submitted data \"' + gs_source_url + '\" is not a valid gsSourceUrl.'
        v = {'response': error_message, 'status': 'error'}
        return tolerant_jsonify(v)

    bucket_and_blob_string = gs_source_url.replace('gs://', '')
    bucket_and_blob_list = bucket_and_blob_string.split('/')
    bucket_name = bucket_and_blob_list.pop(0)
    blob_name = '/'.join(bucket_and_blob_list)

    # instantiate gcp storage client plus with bucket and blob objects
    credentials = service_account.Credentials.from_service_account_info(gcp_json_credentials_dict)
    storage_client = storage.Client(project=gcp_json_credentials_dict['project_id'], credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    try:
        stats = storage.Blob(bucket=bucket, name=blob_name).exists(storage_client)
    except Exception as e:
        error_message = f"""There was an exception trying to do the GCP storage operation
            with the submitted data "{gs_source_url}".
            When GCP tried, it told us: "{str(e)}"
        """
        v = {'response': error_message, 'status': 'error'}
        return tolerant_jsonify(v)
    if stats:
        # if the bucket and blob exist, generate a signed url for the blob...
        # ...and package it as a Hartsfield back-end internal response
        gcp_response = blob.generate_signed_url(
            version='v4',
            expiration=datetime.timedelta(days=7),
            method='GET',
        )
        v = {'response': gcp_response, 'status': 'success'}
    else:
        gcp_response = f'GCP tried, but could not locate a file "{blob_name}" in a bucket called "{bucket_name}".'
        v = {'response': gcp_response, 'status': 'error'}

    return tolerant_jsonify(v)
