

import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


def init(): 
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    # DEVELOPER_KEY = "AIzaSyAjwrlIlQlPbwO_r7iiQRT3vV_BFXQmT68" #lizozom
    DEVELOPER_KEY = os.environ.get("YOUTUBE_API_KEY")

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)
    return youtube

def initOauth(): 
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = os.environ.get("CLIENT_SECRET_FILE_PATH")

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    return googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

