import os

from dotenv import load_dotenv
from supabase import create_client, Client


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# SUPABASE CONFIGURATION
# --------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# --------------------------------------------------
# CREATE SUPABASE CLIENT
# --------------------------------------------------

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("Supabase client initialized")