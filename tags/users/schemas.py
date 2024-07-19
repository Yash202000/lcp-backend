import uuid

from pydantic import BaseModel, EmailStr
from typing import List, Optional, Union, Dict
import datetime

from constants.enums import StatusType, TenantType, UserRoleType


class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: Optional[str] = None
    verification_id: Optional[str] = None
    

    class Config:
        orm_mode = True


class OldNewPassword(BaseModel):
    old_password: str
    new_password: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None



class UserBasic(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    # city : str
    # state : str
    # country: str
    # street_address : str
    # company_name : str
    # zip_code : str
    # job_title : str


    class Config:
        orm_mode = True


class GetUsersResponseAPI(BaseModel):
    status: str
    message: str
    data: List[UserBasic]


class SelectedPlanInfo(BaseModel):
    type: str
    type_alias: TenantType


class PlanInfo(BaseModel):
    selected_plan: SelectedPlanInfo


class UserBase(UserBasic):
    created_at: datetime.datetime
    is_active: Union[bool, None]
    user_role: UserRoleType
    plan_info: PlanInfo

    class Config:
        orm_mode = True


class UserRoleBase(BaseModel):
    id: int
    role: str
    description: str

    class Config:
        orm_mode = True


class TenantBase(BaseModel):
    id: int
    name: str
    alias: str


class UserBaseUserRoleTenant(UserBase):
    user_roles: List[UserRoleBase]
    tenants: List[TenantBase]


class UpdateUserProfile(BaseModel):
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    company_name : Union[str, None] = None
    job_title : Union[str, None] = None
    street_address :Union[str, None] = None
    zip_code : Union[str, None] = None
    city : Union[list, None] = None
    state : Union[list, None] = None
    country : Union[list, None] = None

class UsersWithTotalCount(BaseModel):
    users: List[UserBase]


class UserLoginData(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    access_token: str
    email: str
    # user_role: Optional[str] = UserRoleType


class FlavorBlacklistedDomains(BaseModel):
    flavor: str
    email_domain: str



class ResponseBody(BaseModel):
    status: StatusType
    message: str


class SignUpResponseBody(ResponseBody):
    data: Union[Dict, None] = None


class VerifyUserEmailResponseBody(ResponseBody):
    data: Union[Dict, None] = None


class UserLoginResponseBody(ResponseBody):
    data: Union[Dict, None] = None


class ChangePasswordResponseBody(ResponseBody):
    data: Union[Dict, None] = None


class ForgotPasswordResponseBody(ResponseBody):
    data: Union[Dict, None] = None


class ResetPasswordResponseBody(ResponseBody):
    data: Union[Dict, None] = None


class AddBlacklistDomainsResponseBody(ResponseBody):
    data: Union[Dict, None] = None



class UserProfileResponseBody(ResponseBody):
    data: UserBase


class GoogleLoginToken(BaseModel):
    token: str

class UpdateUserPref(BaseModel):
    user_id : Optional[str]
    tutorial_mode : bool
    onboarding_hints: bool
    color_mode : bool
    help_dialogue : bool
    share_your_filters : bool
    restoration_mode    : bool

class UpdateNotification(BaseModel):
    user_id : Optional[str]
    email_notify_loop_completion : bool = True
    email_notify_dataset_deletion : bool = True
    email_days_before_dataset_deletion : list 

    inplatform_notify_loop_completion : bool 
    inplatform_notify_dataset_deletion : bool
    inplatform_days_before_dataset_deletion : list


