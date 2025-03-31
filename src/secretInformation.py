import os

CLIENT_ID = os.environ.get("CLIENT_ID_AGING_REPORT")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET_AGING_REPORT")
NONPROFIT_TENANT_ID = os.environ.get("NONPROFIT_TENANT_ID")

# Authority URL and scope for Microsoft Graph.
AUTHORITY = f"https://login.microsoftonline.com/{NONPROFIT_TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
