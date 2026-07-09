import os 
from dotenv import load_dotenv

load_dotenv()

# for aws  and openai
# class Config:
#     AWS_ACCESS_KEY =  os.getenv("AWS_ACCESS_KEY")
#     AWS_SECRET_KEY=  os.getenv("AWS_SECRET_KEY")
#     AWS_BUCKET_NAME= os.getenv("AWS_BUCKET_NAME")
#     OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
    

# for euri and supabase furture hugging face can also be used
class Config:
    SUPABASE_URL :str =  os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY :str =  os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY :str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_BUCKET_NAME :str = os.getenv("SUPABASE_BUCKET_NAME")
    EURI_API_KEY :str = os.getenv("EURI_API_KEY")
    EURI_BASE_URL :str = os.getenv("EURI_BASE_URL", "https://api.euron.one/api/v1/euri")
    VECTOR_DB_PATH :str = "/tmp/vector_db" if os.getenv("VERCEL") else os.getenv("VECTOR_DB_PATH", "vector_db")