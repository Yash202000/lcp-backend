from security.settings import settings
from constants.enums import TenantType, FlavorType, CompetitionInvitationStatus, CompetitionWinningCriteriaType


OFFSET_DEFAULT_VALUE = 0
LIMIT_DEFAULT_VALUE = 100

 
MINIMUM_FIRST_NAME_LENGTH = 3
MINIMUM_LAST_NAME_LENGTH = 3
MINIMUM_PASSWORD_LENGTH = 3

PROJECT_QUOTA = 3
PLAN_TYPE_FOR_QUOTA = ['Startup','Freemium','LabelOps']
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


# ---------------------------  UNPROTECTED_END_POINTS -----------------------------------------
UNPROTECTED_END_POINTS_WITH_REQUEST_METHOD = {
    '/openapi.json': 'GET',
    '/admin': 'GET',
    '/favicon.ico': 'GET',
    settings.docs_url: 'GET',
    settings.redocs_url: 'GET',
    '/api/v2/community/google/login': 'GET',
    '/api/v2/community/google/login/verify': 'GET',
    # '/api/v2/pro/google/login': 'GET',
    # '/api/v2/pro/google/login/verify': 'GET',
    # '/api/v2/pro/google/login/token': 'POST',
}
ALLOWED_REQ_METHODS = ['OPTIONS']




PRIVATE_COMPETITION_MINIMUM_NO_OF_PARTICIPANTS = 1
PRIVATE_COMPETITION_MINIMUM_BET_POINTS = 1
ALLOWED_COMPETITION_STATUSES_FOR_STATUS = {
    CompetitionInvitationStatus.YET_TO_ACCEPT.value: [
        CompetitionInvitationStatus.JOINED.value,
        CompetitionInvitationStatus.ACCEPTED.value,
        CompetitionInvitationStatus.REJECTED.value,
        CompetitionInvitationStatus.CANCELLED.value,
    ],
    CompetitionInvitationStatus.JOINED.value: [],
    CompetitionInvitationStatus.ACCEPTED.value: [],
    CompetitionInvitationStatus.REJECTED.value: [],
    CompetitionInvitationStatus.CANCELLED.value: [],
}


COMPETITION_WINNING_CRITERIA_WISE_DETAILS = {
    CompetitionWinningCriteriaType.LESS_DATA_HIGH_COMPRESSION_RATE.value: {
        "name": "Less data with high compression rate to reach performance",
        "alias": CompetitionWinningCriteriaType.LESS_DATA_HIGH_COMPRESSION_RATE.value,
        "is_performance_value_required": True
    },
    CompetitionWinningCriteriaType.BEST_MODEL.value: {
        "name": "Best Model",
        "alias": CompetitionWinningCriteriaType.BEST_MODEL.value,
        "is_performance_value_required": False
    },
    CompetitionWinningCriteriaType.AVERAGE_OF_BOTH.value: {
        "name": "An Average of Both",
        "alias": CompetitionWinningCriteriaType.AVERAGE_OF_BOTH.value,
        "is_performance_value_required": True
    }
}

COMMUNITY_INITIAL_POINTS_USER = 100
COMMUNITY_INITIAL_POINTS_ADMIN = 10000

DEFAULT_TENANT_SCHEMA = "tenant_default"
PUBLIC_TENANT_SCHEMA = "public"


NO_OF_ALLOWED_COMPETITION_EXPERIMENT_SUBMISSIONS = 3
NO_OF_ALLOWED_EXPERIMENT_CREATIONS = 5


experiment_widget_template = [{'acc_per_class':1,
    'accuracy':2,
    'confusion_matrix':3,
    'f1_score':4,
    'label_disagreement':5,
    'precision':6,
    'recall':7,
    'recall_per_class':-1,
    'precision_per_class':-1,
    'n_rec':-1,
    'loop':-1,
    'f1_score_per_class':-1,
    'current_loop':-1}]
