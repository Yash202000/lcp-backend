import enum


class BaseEnum(str, enum.Enum):
    @classmethod
    def values_list(cls):
        return [item.value for item in cls]


class FlavorType(BaseEnum):
    COMMUNITY = "COMMUNITY"
    PRO = "PRO"


class StatusType(BaseEnum):
    SUCCESS = "success"
    ERROR = "error"


class SortKeyType(BaseEnum):
    ASC = "ASC"
    DESC = "DESC"


class ExperimentStatus(BaseEnum):
    NEW = "NEW"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class CloningStatus(BaseEnum):
    IN_PROGRESS = "IN_PROGRESS"
    EXISTS = "EXISTS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExperimentState(BaseEnum):
    START = "START"
    PAUSE = "PAUSE"
    END = "END"
    RESUME = "RESUME"


class ExperimentDataUpdation(BaseEnum):
    NULL = "NULL"
    SINGLE = "SINGLE"
    CONTINUOUS = "CONTINUOUS"


class QueryStrategy(BaseEnum):
    AUTO_AL = "AUTO_AL"  # Automated Data Curation
    PROPRIETARY = "PROPRIETARY"  # ML-Driven Data Curation   -- This class of smart proprietary selection strategies identify the most impactful data analytically.
    DESIGN_OWN = "DESIGN_OWN"  # Rules-Based Data Curation -- Those brute-force selection strategies may be basic but can be powerful for simple problems. They might also take time to tune.
    MANUAL_CURATION = "MANUAL_CURATION"  # Manual Data Curation      -- This feature allows you to manually prioritize data. Perfect to identify biases.
    VIEW_AL = "VIEW_AL" #VIEW_AL -- This method selects the most informative samples for annotation by considering both the viewpoint entropy and the pixel-wise entropy of the unlabeled samples.

class LCPEnvironment(BaseEnum):
    DEV = "DEV"
    PROD = "PROD"


class ProjectType(BaseEnum):
    CURATION = "CURATION"
    LABELING = "LABELING"


class DatasetSource(BaseEnum):
    LIBRARY_ON_PREM = "LIBRARY_ON_PREM"  # Select from LCP’s dataset library # CHeck
    ON_PREM = "ON_PREM"  # Both dataset and model on your premise (local machine)
    HOSTED = "HOSTED"  # Upload new dataset ---> please input the cloud link


class ProjectScope(BaseEnum):
    ALL = "ALL"
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class DatasetHostType(BaseEnum):
    GCP = "GCP"
    S3 = "S3"


class ProjectStarred(BaseEnum):
    STAR = "STAR"
    UNSTAR = "UNSTAR"



