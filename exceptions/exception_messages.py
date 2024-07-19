from fastapi import status
from constants.enums import StatusType


TOKEN_EXPIRED_EXCEPTION = (
    status.HTTP_401_UNAUTHORIZED,
    StatusType.ERROR.value,
    "Token is expired"
)

INVALID_TOKEN_EXCEPTION = (
    status.HTTP_401_UNAUTHORIZED,
    StatusType.ERROR.value,
    "Invalid Token"
)


USER_DOES_NOT_EXIST_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "User does Not Exists"
)


NO_PASSWORD_EXISTS_COMMUNITY_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Please add password for your account or login with google"
)


NO_PASSWORD_EXISTS_PRO_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Please add password for your account or contact admin"
)

INVALID_PASSWORD_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Please check entered credentials"
)

USER_ACCOUNT_NOT_VERIFIED_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Please verify your account or contact admin"
)

USER_NOT_EXISTS_WITH_CREDENTIALS_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Please check entered credentials"
)

UNAUTHORIZED_ACCESS_FOR_USER_ROLE = (
    status.HTTP_403_FORBIDDEN,
    StatusType.ERROR.value,
    "You do not have permissions for this resource"
)

INVALID_FIRST_NAME_LENGTH_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "First Name length must be {} or more"
)

INVALID_LAST_NAME_LENGTH_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Last Name length must be {} or more"
)

INVALID_PASSWORD_LENGTH_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Password length must be {} or more"
)

INVALID_EMAIL_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Invalid Email"
)

BLACKLISTED_EMAIL_DOMAIN_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Your email is not allowed for sign up, please contact admin"
)

EMAIL_ALREADY_EXISTS_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Your email is not allowed for sign up, please contact admin"
)

VERIFIED_USER_TRYING_TO_SIGNUP = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Your email already verified, Please login"
)

NOT_VERIFIED_EXISTING_USER_TRYING_TO_SIGNUP = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Your email already exists, Please verify"
)


SIGNED_UP_USER_TRYING_TO_SIGNUP_AGAIN = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Your email is already registered, please verify or contact admin for any queries"
)

VERIFIED_USER_TRYING_TO_SIGNUP_AGAIN = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Your email is already verified successfully, please login or contact admin for any queries"
)

VERIFIED_USER_TRYING_TO_VERIFY_AGAIN = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Your email is already verified successfully, please login or contact admin for any queries"
)


TENANT_NOT_VERIFIED_BUT_SOMEONE_TRYING_TO_LOGIN = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Your tenant is not verified, please ask them to verify or contact admin for any queries"
)

INVALID_USER_EMAIL_VERIFICATION = (
    status.HTTP_404_NOT_FOUND,
    StatusType.ERROR.value,
    "Invalid user email verification link"
)

INCORRECT_OLD_PASSWORD = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Old password is not correct"
)

NEW_PASSWORD_SAME_AS_OLD_PASSWORD = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "New Password should not be same as old password"
)

EMAIL_DOES_NOT_EXISTS = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Email doesn't exists in the system"
)


INVALID_REQUEST_TO_RESPOND_FOR_INVITATION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "You are not allowed to respond"
)

NO_ACCESS_TO_SUBMIT_EXPERIMENT = (
    status.HTTP_403_FORBIDDEN,
    StatusType.ERROR.value,
    "You are not allowed to submit experiment for this competition"
)

INVALID_REQUEST_TO_UPDATE_INVITATION_STATUS = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Invalid request to update the invitation_status"
)

USER_EMAIL_NOT_VERIFIED = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Please verify your email"
)

USER_TRYING_TO_MANIPULATE_JWT_TOKEN = (
    status.HTTP_403_FORBIDDEN,
    StatusType.ERROR.value,
    "Invalid Access Token"
)

INVALID_DATABASE_QUERY_EXCEPTION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    """Database Error: exception_type: {}, exception_value: {}, stack_trace: {}"""
)

UNWANTED_BEHAVIOUR = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Unwanted behaviour, contact admin or please try again"
)

REQUIRED_FIELDS_ARE_MISSING = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Invalid {}"
)


INVALID_TIMEZONE_REGION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Invalid Timezone region"
)

USER_EXCEEDED_THE_LIMIT_OF_EXPERIMENT_SUBMISSION = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "You have exceeded the limit of experiment submissions"
)

USER_EXCEEDED_THE_LIMIT_OF_EXPERIMENT_CREATIONS = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "You have exceeded the limit of experiment creations"
)

NO_ACCESS_TO_CREATE_EXPERIMENT = (
    status.HTTP_403_FORBIDDEN,
    StatusType.ERROR.value,
    "You are not allowed to create experiment for this competition"
)



INSUFFICIENT_USER_POINTS = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "You don't have enough points to redeem the product"
)

RECEIVER_EMAIL_IS_MISSING = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Please add email to which gift card should be sent"
)

INVALID_USER_ADDRESS_ID = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Invalid address id is given"
)

RECEIVER_ADDRESS_SHOULD_BE_GIVEN = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "No address is selected"
)

EMAIL_SENDING_ERROR = (
    status.HTTP_400_BAD_REQUEST,
    StatusType.ERROR.value,
    "Cannot send the email because {}. Please contact support"
)
