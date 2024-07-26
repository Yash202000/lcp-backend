# -------------------------------- Python imports ---------------------------
import pathlib

# -------------------------------- FastAPI imports ---------------------------
from fastapi_mail import ConnectionConfig

# -------------------------------- Pydantic imports ---------------------------
from pydantic_settings import BaseSettings


# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Token
    JWT_SECRET                   : str   
    ALGORITHM                    : str   
    ACCESS_TOKEN_EXPIRE_MINUTES  : int
    EMAIL_ACCESS_TOKEN_EXPIRE_MINUTES: int   
    TEMPORARY_EXPIRE_MINUTES     : int
    TOKEN_URL                    : str
    
    # Swagger 
    docs_url                     : str
    redocs_url                   : str
    # admin_url                    : str
    DATABASE_URL                 : str
    N_DATABASE_URL               : str
    N_URL                        : str
    # DATABASE_URL_COMMUNITY       : str
    
    # Mail 
    MAIL_USERNAME                : str          
    MAIL_PASSWORD                : str
    MAIL_FROM                    : str
    MAIL_PORT                    : int
    MAIL_SERVER                  : str
    MAIL_STARTTLS                     : bool
    MAIL_SSL_TLS                     : bool
    USE_CREDENTIALS              : bool
    TEMPLATE_FOLDER              : str
    SEND_EMAIL_TO_RESET_PASSWORD : str
    SEND_EMAIL_FOR_VERIFICATION  : str

    # # Flavor
    # CURRENT_FLAVOR: str

    # # Google Auth
    # GOOGLE_CLIENT_ID: str
    # GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str

    # # Domain Name or IP
    # PROTOCOL: str
    # DOMAIN_NAME: str


    # # Credentials 
    # TYPE                        :  str              
    # PROJECT_ID                  :  str
    # PRIVATE_KEY_ID              :  str
    # PRIVATE_KEY                 :  str
    # CLIENT_EMAIL                :  str
    # CLIENT_ID                   :  str
    # AUTH_URI                    :  str
    # TOKEN_URI                   :  str
    # AUTH_PROVIDER_X509_CERT_URL :  str
    # CLIENT_X509_CERT_URL        :  str

    # # Platform Backend
    # CLIENT_ID_PLATFORM_BACKEND     : str
    # CLIENT_SECRET_PLATFORM_BACKEND : str

    # # GCP 
    # GCP_ANNOTATION_BUCKET        : str
    # ROOT_BUCKET                  : str
    # TEMP_BUCKET                  : str
    # GCP_CONTENT_TYPE             : str
    # TEMP_BUCKET                  : str
    
    # # REDIS CREDENTIALS
    # REDIS_HOST                   :  str
    # REDIS_PORT                   :  str
    # REDIS_USERNAME               :  str
    # REDIS_PASSWORD               :  str
    # REDIS_COMMIT_DB              :  int
    # REDIS_STASH_DB               :  int

    # DELTA_LAKE_STORAGE_URL       :  str
    # PUBLIC_DATASET_BASE_URL      :  str
    # PUBLIC_DATASET_ROOT_BUCKET   :  str

    # PROJECT_DIR: str
    DB_ECHO: str

    # GCP_CREDS_FILE: str  

    class Config:
        case_sensitive  =  True
        env_file        =  ".env"


settings = Settings()

settings.DB_ECHO = eval(settings.DB_ECHO)


conf = ConnectionConfig(
    MAIL_USERNAME      =    settings.MAIL_USERNAME,
    MAIL_PASSWORD      =    settings.MAIL_PASSWORD,
    MAIL_FROM          =    settings.MAIL_FROM,
    MAIL_PORT          =    settings.MAIL_PORT,
    MAIL_SERVER        =    settings.MAIL_SERVER,
    MAIL_STARTTLS      =    settings.MAIL_STARTTLS,
    MAIL_SSL_TLS       =    settings.MAIL_SSL_TLS,
    USE_CREDENTIALS    =    settings.USE_CREDENTIALS,
    TEMPLATE_FOLDER    =    settings.TEMPLATE_FOLDER,
)
