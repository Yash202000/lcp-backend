# -------------------------------- Python imports ---------------------------
import uuid
from typing import Union, Dict, List
import datetime

# -------------------------------- FastAPI imports ---------------------------
from fastapi import APIRouter, Depends, status, HTTPException, Request, Body
from fastapi.encoders import jsonable_encoder
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

# -------------------------------- sqlalchemy imports ---------------------------
import sqlalchemy
from pydantic import EmailStr
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# --------------------------------  database imports ---------------------------
from database import SessionLocal, engine
from db_connections import get_db_session_with_public_schema, get_public_schema_db, \
    get_db_session_with_schema, get_db_engine_connectable_with_schema, get_db
from exceptions.exception_messages import \
    SIGNED_UP_USER_TRYING_TO_SIGNUP_AGAIN, INVALID_USER_EMAIL_VERIFICATION, INVALID_EMAIL_EXCEPTION, \
    VERIFIED_USER_TRYING_TO_SIGNUP_AGAIN, UNWANTED_BEHAVIOUR, EMAIL_SENDING_ERROR

# --------------------------------  users imports ------------------------------
from security.authentication import (
    get_password_hash,
    create_access_token,
    authenticate,
    verify_password,
    decode_token,
    oauth2_scheme,
)
from models.public.public_models import  UserRole, User
# from models.public_models import Tenant, BlacklistedEmailDomain
from tags.users import schemas

from constants.enums import StatusType

from constants.enums import SortKeyType, FlavorType
from constants.plain_constants import MINIMUM_FIRST_NAME_LENGTH, MINIMUM_LAST_NAME_LENGTH, MINIMUM_PASSWORD_LENGTH
# from data_seeding_scripts.tenant_models_scripts.load_default_data_in_tenant_tables import load_default_data_in_tenant_tables
# from tags.users.common_methods import create_user_points
from tags.users.schemas import FlavorBlacklistedDomains, UpdateNotification
# from utils.alembic_utils import alembic_upgrade_for_single_tenant

from utils.email_utils import send_email_for_verification, send_email_to_reset_password, is_valid_email
from utils.get_random_id_string import get_random_uuid_string_for_primary_key
# from utils.user_role_utils.role_based_permissions import super_admin, tenant_admin, public, \
    # get_user_role_for_role_id_tenant_schema, get_user_role_for_user_id, get_id_of_role

from exceptions.custom_exceptions import CustomException
from exceptions.prepare_custom_exception_message import raise_invalid_db_query_error
# from utils.create_tenant_bucket import create_tenant_folder_in_root_bucket




user_router = APIRouter(
    prefix="/api",
    tags=['Users']
)


def get_user_by_email(db: Session, email: str):
    print('get user for email if exist')
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: schemas.User, verification_id: str ):
    password = get_password_hash(user.password)
    db_user = User(email=user.email, first_name=user.first_name, last_name=user.last_name, password =password, verification_id=verification_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@user_router.post("/users/", response_model=schemas.User)
def create_new_user(user: schemas.User, db: Session = Depends(get_db)):
    print("inside the controller", user)
    verification_id = get_random_uuid_string_for_primary_key()
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        print(db_user.verification_id, " : ", db_user.email)
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user =  create_user(db=db, user=user,verification_id=verification_id)
    return schemas.User(first_name=user.first_name, last_name=user.last_name, email = user.email, password=None, verification_id=user.verification_id)
    
    

@user_router.get(
    '/v1/email/{email}/verify/{verification_code}', summary="Email Verification",
    status_code=status.HTTP_202_ACCEPTED, response_model=schemas.VerifyUserEmailResponseBody)
def verify_user_email(
        request: Request, verification_code: str, email: str, db: Session = Depends(get_db)
):
    """
        This Endpoint will get verification_id which is sent from tenant email
        If verification_id is not correct raise Exception
        otherwise create schema with all tables and make is_verified Flag to True
    """
    
    db_user = db.query(User).filter(User.verification_id == verification_code).first()
    if db_user.is_verified == False and db_user.verification_id==verification_code:
        db_user.is_verified = True
        db_user.verification_id = None
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return  schemas.VerifyUserEmailResponseBody(
            status=StatusType.SUCCESS.value,
            message="Your email address is verified successfully."
        )
    elif db_user.is_verified == True :
        return  schemas.VerifyUserEmailResponseBody(
            status=StatusType.SUCCESS.value,
            message="Your email address is already verified."
        )
    else:
        return schemas.VerifyUserEmailResponseBody(
            status=StatusType.ERROR.value,
            message="unexpected behavious"
        )
        
        

    
    
    
@user_router.post(
    "/v1/users/login", summary="Login user - web", status_code=status.HTTP_200_OK,
    response_model=schemas.UserLoginResponseBody
)
def user_login_web(
        request: Request, user_data: schemas.UserLoginData,
        db: Session = Depends(get_db_session_with_public_schema)
):
    """
       This Endpoint will take username ,password from request body then return access token
    """
    print('insdie the userlogin web ')
    return user_login(request=request, user_data=dict(user_data), db=db)
    


@user_router.post(
    "/v1/users/login/swagger", summary="Login user - swagger", status_code=status.HTTP_200_OK,
    # response_model=schemas.UserLoginResponseBody
)
def user_login_swagger(request: Request, body: OAuth2PasswordRequestForm = Depends(),
                       db: Session = Depends(get_db_session_with_public_schema)):
    """
       This Endpoint will take username ,password from request body then return access token
    """
    user_data = jsonable_encoder(body)
    user_data["email"] = user_data["username"]
    user_login_response = user_login(request=request, user_data=user_data, db=db)
    return user_login_response



def user_login(request: Request, user_data: Dict, db: Session):
    user_email = user_data["email"]

    if not is_valid_email(user_email):
        raise CustomException(*INVALID_EMAIL_EXCEPTION)
    

    user_password = user_data['password']
    
    user, tenant_schema , error= authenticate(
         email=user_email, password=user_password, db=db
    )
    
    if error!=None:
        return schemas.UserLoginResponseBody(
            status=StatusType.ERROR.value,
            message="check password ",
            data=None
        )
        
    client_host = None
    try:
        client_host = request.client.host
    except Exception:
        pass

    
    try:
        # try to get client address
        current_datetime = datetime.datetime.utcnow()
        user.last_login_at = current_datetime
        user.last_login_ip = client_host

        db.add(user)
        db.commit()
        user_id = user.id
        user_email = user.email
    except SQLAlchemyError as err:
        raise_invalid_db_query_error(err)

    access_token = create_access_token(
        user_id=user_id, email=user_email,
    )
    
    user_login_response = schemas.UserLoginResponse(
        access_token=access_token, email=user_email,
    )
    
    return schemas.UserLoginResponseBody(
            status=StatusType.SUCCESS.value,
            message="Login success!",
            data=dict(user_login_response)
        )




@user_router.post(
    "/v1/users/change_password", summary="Update User Password",
    status_code=status.HTTP_200_OK, response_model=schemas.ChangePasswordResponseBody,
    dependencies=[Depends(oauth2_scheme)]
)
def change_user_password(
        request: Request, old_new_password: schemas.OldNewPassword,
        db: Session = Depends(get_db)
):
    print("inside teh change user password function.")
    """
        This Endpoint will take old_password ,new_password from request body then reset the password and return a mgs
    """
    from exceptions.exception_messages import \
        INCORRECT_OLD_PASSWORD, NEW_PASSWORD_SAME_AS_OLD_PASSWORD, INVALID_PASSWORD_LENGTH_EXCEPTION

    old_password = old_new_password.old_password
    new_password = old_new_password.new_password
    # if New password is same as old password then raise Exception
    if old_password == new_password:
        raise HTTPException(*NEW_PASSWORD_SAME_AS_OLD_PASSWORD)

    # if New password length is not satisfied, raise Exception
    if len(new_password) < MINIMUM_PASSWORD_LENGTH:
        custom_message = list(INVALID_PASSWORD_LENGTH_EXCEPTION)
        custom_message[2] = custom_message[2].format(MINIMUM_PASSWORD_LENGTH)
        raise CustomException(*custom_message)

    current_user = request.state.user

    # if old password is not correct raise Exception
    if not verify_password(old_password, current_user.password):
        raise CustomException(*INCORRECT_OLD_PASSWORD)

    update_user_password(request,user_id=current_user.id, db=db, new_password=new_password)

    response = schemas.ChangePasswordResponseBody(
        status=StatusType.SUCCESS.value,
        message="Successfully Updated the Password !"
    )
    return response


def update_user_password(request:Request,user_id: str, new_password: str, db: Session):
    password_hash = get_password_hash(new_password)

    try:
        # Updating user password
        user_object = db.query(User).get(user_id)
        user_object.password = password_hash

        db.add(user_object)
        db.commit()
        # todo need to know after this commit we cant refresh user
    except SQLAlchemyError as err:
        raise_invalid_db_query_error(err)