from supabase import create_client
from config import Config 
from io import BytesIO
from utils.logger import get_logger

logger = get_logger(__name__)

class SupabaseStorage:
    def __init__(self):
        logger.info(f"Initializing SupabaseStorage client with bucket: '{Config.SUPABASE_BUCKET_NAME}'")
        self.client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_SERVICE_ROLE_KEY
        )

        self.bucket = Config.SUPABASE_BUCKET_NAME

    def uploadfile(self,file_obj,file_name):
        logger.info(f"Uploading file '{file_name}' to Supabase bucket '{self.bucket}'")
        try:
            file_obj.seek(0)
            self.client.storage.from_(self.bucket).upload(
                path = file_name,
                file = file_obj.read(),
                file_options = {
                    "content-type": "application/octet-stream",
                    "upsert": "true",
                },
            )
            logger.debug(f"Successfully uploaded '{file_name}' to storage.")
            return True
        except Exception as e:
            logger.error(f"Error uploading file '{file_name}' to Supabase: {str(e)}", exc_info=True)
            return False
        
    def get_file(self, filename):
        logger.info(f"Retrieving file '{filename}' from Supabase bucket '{self.bucket}'")
        try:
            data = self.client.storage.from_(self.bucket).download(filename)
            logger.debug(f"Successfully retrieved '{filename}' from storage.")
            return BytesIO(data)
        except Exception as e:
            logger.error(f"Error retrieving file '{filename}' from Supabase: {str(e)}", exc_info=True)
            return None

    def list_files(self):
        logger.info(f"Listing files from Supabase bucket '{self.bucket}'")
        try:
            res = self.client.storage.from_(self.bucket).list()
            filenames = [item['name'] for item in res if item['name'] != '.emptyFolderPlaceholder']
            logger.debug(f"Retrieved files from storage: {filenames}")
            return filenames
        except Exception as e:
            logger.error(f"Error listing files from Supabase: {str(e)}", exc_info=True)
            return []


    































# import boto3 
# from botocore.exceptions import ClientError
# from config import Config

# class S3Storage:
#     def __init__(self):
#         self.s3 = boto3.client(
            
#             "s3",
#             aws_access_key_id=Config.AWS_ACCESS_KEY,
#             aws_secret_access_key=Config.AWS_SECRET_KEY
#         )

        
#         self.bucket = Config.AWS_BUCKET_NAME

#     def upload_file(self,file_obj,file_name):
#         try:
#             self.s3.upload_fileobj(file_obj,self.bucket,file_name)
#             return True
#         except ClientError as e:
#             print(f"Error uploading file: {e}")
#             return False
        
    
#     def get_file(self,filename):
#         try:
#             response = self.s3.get_object(Bucket = self.bucket, key =filename)
#             return response['Body']
        
#         except ClientError as e:
#             print(f"Error retrieving file: {e}")
#             return None
        

