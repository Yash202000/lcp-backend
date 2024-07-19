# -------------------------------- Python imports ---------------------------
from datetime import datetime, timedelta

# -------------------------------- FastAPI imports ---------------------------
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request

# -------------------------------- sqlalchemy imports ---------------------------
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# -------------------------------- JWT imports ---------------------------
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError

# -------------------------------- db imports ---------------------------
from db_connections import get_db_session_with_public_schema, get_db_session_with_schema, get_public_schema_db
from exceptions.custom_exceptions import CustomException
from exceptions.exception_messages import USER_TRYING_TO_MANIPULATE_JWT_TOKEN

# --------------------------------  users imports ------------------------------
from models.public.public_models import User
from security.settings import settings


from exceptions.prepare_custom_exception_message import raise_invalid_db_query_error

# =====================================  User Verification PART ========================================
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)


def authenticate(email: str, password: str, db: Session):
    from exceptions.exception_messages import \
        NO_PASSWORD_EXISTS_PRO_EXCEPTION, NO_PASSWORD_EXISTS_COMMUNITY_EXCEPTION, INVALID_PASSWORD_EXCEPTION, \
        USER_ACCOUNT_NOT_VERIFIED_EXCEPTION, USER_NOT_EXISTS_WITH_CREDENTIALS_EXCEPTION, \
        TENANT_NOT_VERIFIED_BUT_SOMEONE_TRYING_TO_LOGIN, USER_EMAIL_NOT_VERIFIED
    
    user = None
    try:
        user = db.query(User).filter(User.email == email).first()
    except SQLAlchemyError as err:
        raise_invalid_db_query_error(err)
    db.close()

    if not user:
        return None , None , USER_NOT_EXISTS_WITH_CREDENTIALS_EXCEPTION

    if not user.password:
        custom_message = NO_PASSWORD_EXISTS_PRO_EXCEPTION
        return None , None ,custom_message

    if not user.is_verified:
        return None , None , USER_ACCOUNT_NOT_VERIFIED_EXCEPTION

    if not verify_password(password, user.password):
        print("inside tehe verify password", verify_password(password, user.password) )
        return None , None , INVALID_PASSWORD_EXCEPTION
    
    print("inside tehe verify password")

    return user, 'public', None


# ===================================== End ========================================


# =====================================  JWT AUTHENICATION PART ========================================
def create_access_token_temporary(user_id: str,tenant_schema: str, token_type="access_token"):
        lifetime    =      timedelta(minutes=settings.TEMPORARY_EXPIRE_MINUTES)
        expire      =      datetime.utcnow() + lifetime
        payload     =      {
            "type"         : token_type,
            "iat"          : datetime.utcnow(),
            "exp"          : expire,
             "user_id"     : user_id,
            "tenant_schema": tenant_schema
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)



def create_access_token(
        user_id: str, email: str, token_type="access_token", for_forgot_password=False
):
    print("insid eht access create access token function.")
    """
       this function will create access token for given user_id & email
    """

    if for_forgot_password:
        lifetime = timedelta(minutes=settings.EMAIL_ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        lifetime = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now() + lifetime
    payload = {
        "type": token_type,
        "exp": expire,
        "iat": datetime.now(),
        "user_id": user_id,
        "email": email,
    }
    
    print("here to encode ", payload)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def decode_token(token):
    """
       this function will decode access token and return user_id
    """
    from exceptions.exception_messages import TOKEN_EXPIRED_EXCEPTION, INVALID_TOKEN_EXCEPTION

    if not token:
        return None, None
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=settings.ALGORITHM)
        user_id = payload.get("user_id")
        # tenant_schema might be None too in case of tenant resetting password
        tenant_schema = payload.get("tenant_schema")
        if user_id is None:
            raise CustomException(*INVALID_TOKEN_EXCEPTION)
        return user_id, tenant_schema
    except ExpiredSignatureError:
        raise CustomException(*TOKEN_EXPIRED_EXCEPTION)
    except JWTError:
        raise CustomException(*INVALID_TOKEN_EXCEPTION)


class OAuth2PasswordBearerCustom(OAuth2PasswordBearer):
    def __init__(self, token_url):
        super(OAuth2PasswordBearerCustom, self).__init__(tokenUrl=token_url)

    async def __call__(self, request: Request):
        from exceptions.exception_messages import \
            USER_DOES_NOT_EXIST_EXCEPTION, TOKEN_EXPIRED_EXCEPTION, INVALID_TOKEN_EXCEPTION
            
        

        res = await super().__call__(request)
        res = res.replace('Bearer', '')
        res = res.replace(' ', '')
        try:
            payload = jwt.decode(res, settings.JWT_SECRET, algorithms=settings.ALGORITHM)
            user_id = payload.get("user_id")

            # if super_admin comes into play we might have to change using tenant_schema here
            if not user_id:
                raise CustomException(*INVALID_TOKEN_EXCEPTION)

            
            db_session = get_public_schema_db()
            user = None
            try:
                user = db_session.query(User).filter(User.id == user_id).first()
            except SQLAlchemyError as err:
                raise_invalid_db_query_error(err)

            db_session.close()

            if not user:
                raise CustomException(*USER_DOES_NOT_EXIST_EXCEPTION)

            # appending user data to request state
            request.state.user = user
            return user

        except ExpiredSignatureError:
            raise CustomException(*TOKEN_EXPIRED_EXCEPTION)
        except JWTError:
            raise CustomException(*INVALID_TOKEN_EXCEPTION)


oauth2_scheme = OAuth2PasswordBearerCustom(token_url=settings.TOKEN_URL)





# ===================================== END JWT AUTHENTICATION PART ========================================
