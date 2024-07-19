import datetime
import json
import uuid
from typing import Dict

import requests
from fastapi import APIRouter, Depends
from fastapi import Request
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.orm import Session

from starlette.config import Config

from constants.plain_constants import LCP_COMMUNITY_TENANT
from constants.enums import StatusType, FlavorType, UserRoleType
from db_connections import get_db_session_with_public_schema, get_db_session_with_schema
from exceptions.custom_exceptions import CustomException
from exceptions.exception_messages import BAD_REQUEST_TO_USE_GOOGLE_FOR_SIGNUP_LOGIN
from exceptions.prepare_custom_exception_message import raise_invalid_db_query_error
from models.public_models import Tenant
from models.common.common_models import User
from security.settings import settings
from security.authentication import create_access_token
from tags.users import schemas as user_schemas

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError

from tags.users.common_methods import create_user_points
from tags.users.routes import create_LCP_community_tenant, create_tables_for_schema, \
    seed_default_data_in_tenant_tables, add_default_role_for_tenant_user, enable_tenant_type_for_tenant, \
    validate_is_email_domain_blacklisted_for_flavor
from tags.users.schemas import GoogleLoginToken
from utils.get_random_id_string import get_random_uuid_string_for_primary_key
from utils.user_role_utils.role_based_permissions import get_user_role_for_user_id

router_prefix = f"/api/v2/{settings.CURRENT_FLAVOR.lower()}/google"

# router
google_auth_router = APIRouter(
    prefix=router_prefix,
    tags=['Google Auth']
)

# Set up Google OAuth
config_data = {'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': settings.GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


# todo useful for backend webserver verification
@google_auth_router.get('/login')
async def google_login(request: Request):
    redirect_uri = f"{settings.PROTOCOL}://{settings.DOMAIN_NAME}{router_prefix}/login/verify"
    return await oauth.google.authorize_redirect(request, redirect_uri)


# todo useful for backend webserver verification
@google_auth_router.get('/login/verify', response_model=user_schemas.UserLoginResponseBody)
async def google_login_verify(request: Request, db: Session = Depends(get_db_session_with_public_schema)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise CustomException(*BAD_REQUEST_TO_USE_GOOGLE_FOR_SIGNUP_LOGIN)

    if not token["access_token"]:
        raise CustomException(*BAD_REQUEST_TO_USE_GOOGLE_FOR_SIGNUP_LOGIN)

    google_user_data = await oauth.google.parse_id_token(request, token)
    if not google_user_data:
        raise CustomException(*BAD_REQUEST_TO_USE_GOOGLE_FOR_SIGNUP_LOGIN)

    user_data = {
        "first_name": google_user_data["given_name"],
        "last_name": google_user_data["family_name"],
        "email": google_user_data["email"]
    }

    response = await google_login_verify_user_response(db, user_data)
    return response


@google_auth_router.post('/login/token', response_model=user_schemas.UserLoginResponseBody)
async def google_login_verify_with_token(
        request: Request,
        google_login_email_token: GoogleLoginToken,
        db: Session = Depends(get_db_session_with_public_schema)
):
    get_user_profile_url = "https://www.googleapis.com/drive/v3/about?fields=user&access_token=" + google_login_email_token.token
    payload = {}
    headers = {}
    try:
        response = requests.get(get_user_profile_url, headers=headers, data=payload)
    except:
        raise CustomException(*BAD_REQUEST_TO_USE_GOOGLE_FOR_SIGNUP_LOGIN)

    user_details = json.loads(response.text)["user"]

    user_data = {
        "first_name": user_details["displayName"].split(' ')[0],
        "last_name": user_details["displayName"].split(' ')[1],
        "email": user_details["emailAddress"],
        "image_url": user_details["photoLink"]
    }

    flavor = settings.CURRENT_FLAVOR
    user_email_domain = user_data["email"].split('@')[1]
    validate_is_email_domain_blacklisted_for_flavor(
        flavor=flavor, user_email_domain=user_email_domain, db=db
    )

    response = await google_login_verify_user_response(flavor=request.state.flavor, db=db, user_data=user_data)
    return response


async def google_login_verify_user_response(flavor: str, db: Session, user_data: Dict):
    # flavor = settings.CURRENT_FLAVOR
    tenant_email_domain = None
    if flavor == FlavorType.COMMUNITY.value:
        tenant_email_domain = LCP_COMMUNITY_TENANT["email_domain"]
    elif flavor == FlavorType.PRO.value:
        tenant_email_domain = user_data["email"].split('@')[1]
    tenant = db.query(Tenant).filter(Tenant.email_domain == tenant_email_domain).first()
    tenant_id = None
    tenant_user_id = None
    tenant_schema = None
    is_user_not_created_or_found = False
    if not tenant and flavor == FlavorType.COMMUNITY.value:
        is_community_tenant_admin_signing_up = user_data["email"] == LCP_COMMUNITY_TENANT["email"]
        if is_community_tenant_admin_signing_up:
            LCP_COMMUNITY_TENANT["first_name"] = user_data["first_name"]
            LCP_COMMUNITY_TENANT["last_name"] = user_data["last_name"]
            LCP_COMMUNITY_TENANT["email"] = user_data["email"]

        tenant_id, tenant_user_id, tenant_schema = create_LCP_community_tenant(db=db)

        if is_community_tenant_admin_signing_up:
            is_user_not_created_or_found = True

    elif not tenant and flavor == FlavorType.PRO.value:
        # create verified tenant and tenant_admin user too
        tenant_user_id, tenant_schema = create_verified_tenant_along_with_tables_creation(
            db=db, flavor=flavor, user_data=user_data, email_domain=tenant_email_domain
        )
        is_user_not_created_or_found = True
    else:
        tenant_schema = tenant.schema
        tenant_id = tenant.id

    if not is_user_not_created_or_found:
        db_session = get_db_session_with_schema(flavor, schema=tenant_schema)

        tenant_user_obj = db_session.query(User).filter(User.email == user_data["email"]).first()
        if tenant_user_obj:
            tenant_user_id = tenant_user_obj.id
        else:
            tenant_user_id = create_verified_tenant_user_with_user_role(
                user_data=user_data, tenant_schema=tenant_schema, db=db_session
            )
            if flavor == FlavorType.COMMUNITY.value:
                create_user_points(db=db_session, user_ids=[tenant_user_id])

        db_session.close()
    db_session = get_db_session_with_schema(flavor,schema=tenant_schema)
    user_role = get_user_role_for_user_id(user_id=tenant_user_id, db=db_session)
    db_session.close()
    user_email = user_data["email"]
    access_token = create_access_token(
        user_id=tenant_user_id, email=user_email, tenant_schema=tenant_schema
    )
    user_login_data = user_schemas.UserLoginResponse(
        access_token=access_token, email=user_email, user_role=user_role
    )
    response = user_schemas.UserLoginResponseBody(
        status=StatusType.SUCCESS.value,
        message="Successfully logged in",
        data=user_login_data
    )
    return response


def create_verified_tenant_along_with_tables_creation(
        db: Session, flavor: FlavorType, user_data: Dict, email_domain: str
):
    tenant_schema, tenant_user_id = create_verified_tenant(flavor=flavor,
        db=db, tenant_data=user_data, tenant_email_domain=email_domain)
    db_session = get_db_session_with_schema(flavor, schema=tenant_schema)

    seed_default_data_in_tenant_tables(
        db=db_session, tenant_schema=tenant_schema, flavor=flavor, created_by_user_id=tenant_user_id)
    add_default_role_for_tenant_user(
        db=db_session, user_id=tenant_user_id, user_role=UserRoleType.TENANT_ADMIN.value)
    enable_tenant_type_for_tenant(
        db=db_session, flavor=flavor, email_domain=email_domain, updated_by_user_id=tenant_user_id)

    db_session.close()

    return tenant_user_id, tenant_schema


def create_verified_tenant(flavor: str,db: Session, tenant_data: Dict, tenant_email_domain: str):

    # Creating verified tenant data
    random_id = uuid.uuid4().hex[:8]
    tenant_mail_server, tenant_mail_domain = tenant_email_domain.split(".")
    tenant_schema = tenant_mail_server + "_" + tenant_mail_domain + "_" + random_id

    is_verified = True
    current_datetime =  datetime.datetime.utcnow()
    tenant_id = get_random_uuid_string_for_primary_key()
    try:
        tenant_obj = Tenant(
            id=tenant_id,
            first_name=tenant_data["first_name"],
            last_name=tenant_data["last_name"],
            email=tenant_data["email"],
            schema=tenant_schema,
            email_domain=tenant_email_domain,
            is_verified=is_verified,
            verified_at=current_datetime,
        )
        db.add(tenant_obj)
        db.commit()
        tenant_data = tenant_obj.__dict__
    except SQLAlchemyError as err:
        raise_invalid_db_query_error(err)

    # creating tenant tables for schema
    create_tables_for_schema(schema=tenant_schema)

    try:
        db_session = get_db_session_with_schema(flavor = flavor,schema=tenant_schema)
        # creating a user(tenant_user) under tenant
        tenant_user_id = get_random_uuid_string_for_primary_key()
        db_session.add(User(
            id=tenant_user_id,
            first_name=tenant_data["first_name"],
            last_name=tenant_data["last_name"],
            email=tenant_data["email"],
            tenant_schema=tenant_schema,
            is_verified=tenant_data["is_verified"],
            verified_at=tenant_data["verified_at"]
        ))

        db_session.commit()
        db_session.close()

        return tenant_schema, tenant_user_id
    except SQLAlchemyError as err:
        raise_invalid_db_query_error(err)


def create_verified_tenant_user_with_user_role(db: Session, tenant_schema: str, user_data: Dict):
    tenant_user_id = create_verified_tenant_user(tenant_schema=tenant_schema, user_data=user_data, db=db)
    add_default_role_for_tenant_user(db=db, user_id=tenant_user_id, user_role=UserRoleType.USER.value)

    return tenant_user_id


def create_verified_tenant_user(tenant_schema: str, user_data: Dict, db: Session):
    import datetime

    is_verified = True
    verified_at = datetime.datetime.now()

    user_id = get_random_uuid_string_for_primary_key()
    user = User(
        id=user_id,
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        email=user_data["email"],
        tenant_schema=tenant_schema,
        is_verified=is_verified,
        verified_at=verified_at
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user_id
