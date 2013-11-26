"""
This config file runs the simplest dev environment using sqlite, and db-based
sessions. Assumes structure:

/envroot/
        /db   # This is where it'll write the database file
        /mitx # The location of this repo
        /log  # Where we're going to write log files
"""

# We intentionally define lots of variables that aren't used, and
# want to import all variables from base settings files
# pylint: disable=W0401, W0614

from .common import *
import os
from path import path
from warnings import filterwarnings

os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'localhost:8000-9000'

# can't test start dates with this True, but on the other hand,
# can test everything else :)
MITX_FEATURES['DISABLE_START_DATES'] = True

# Most tests don't use the discussion service, so we turn it off to speed them up.
# Tests that do can enable this flag, but must use the UrlResetMixin class to force urls.py
# to reload
MITX_FEATURES['ENABLE_DISCUSSION_SERVICE'] = False

MITX_FEATURES['ENABLE_SERVICE_STATUS'] = True

MITX_FEATURES['ENABLE_HINTER_INSTRUCTOR_VIEW'] = True

MITX_FEATURES['ENABLE_INSTRUCTOR_BETA_DASHBOARD'] = True

MITX_FEATURES['ENABLE_SHOPPING_CART'] = True

# Enable this feature for course staff grade downloads, to enable acceptance tests
# (presumably, we'll shortly enable this in prod and remove this feature flag)
MITX_FEATURES['ENABLE_S3_GRADE_DOWNLOADS'] = True
MITX_FEATURES['ALLOW_COURSE_STAFF_GRADE_DOWNLOADS'] = True

# Need wiki for courseware views to work. TODO (vshnayder): shouldn't need it.
WIKI_ENABLED = True

# Makes the tests run much faster...
SOUTH_TESTS_MIGRATE = False  # To disable migrations and use syncdb instead

# Nose Test Runner
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

_system = 'lms'

_report_dir = REPO_ROOT / 'reports' / _system
_report_dir.makedirs_p()

NOSE_ARGS = [
    '--id-file', REPO_ROOT / '.testids' / _system / 'noseids',
    '--xunit-file', _report_dir / 'nosetests.xml',
]

# Local Directories
TEST_ROOT = path("test_root")
# Want static files in the same dir for running on jenkins.
STATIC_ROOT = TEST_ROOT / "staticfiles"

STATUS_MESSAGE_PATH = TEST_ROOT / "status_message.json"

COURSES_ROOT = TEST_ROOT / "data"
DATA_DIR = COURSES_ROOT

COMMON_TEST_DATA_ROOT = COMMON_ROOT / "test" / "data"
# Where the content data is checked out.  This may not exist on jenkins.
GITHUB_REPO_ROOT = ENV_ROOT / "data"


XQUEUE_INTERFACE = {
    "url": "http://sandbox-xqueue.edx.org",
    "django_auth": {
        "username": "lms",
        "password": "***REMOVED***"
    },
    "basic_auth": ('anant', 'agarwal'),
}
XQUEUE_WAITTIME_BETWEEN_REQUESTS = 5  # seconds


# Don't rely on a real staff grading backend
MOCK_STAFF_GRADING = True
MOCK_PEER_GRADING = True

# TODO (cpennington): We need to figure out how envs/test.py can inject things
# into common.py so that we don't have to repeat this sort of thing
STATICFILES_DIRS = [
    COMMON_ROOT / "static",
    PROJECT_ROOT / "static",
]
STATICFILES_DIRS += [
    (course_dir, COMMON_TEST_DATA_ROOT / course_dir)
    for course_dir in os.listdir(COMMON_TEST_DATA_ROOT)
    if os.path.isdir(COMMON_TEST_DATA_ROOT / course_dir)
]

# point tests at the test courses by default

MODULESTORE = {
    'default': {
        'ENGINE': 'xmodule.modulestore.xml.XMLModuleStore',
        'OPTIONS': {
            'data_dir': COMMON_TEST_DATA_ROOT,
            'default_class': 'xmodule.hidden_module.HiddenDescriptor',
        }
    }
}

# Starting modulestores generates log messages.  If we wait to init modulestores,
# then those messages will be silenced by the test runner.
INIT_MODULESTORE_ON_STARTUP = False

CONTENTSTORE = {
    'ENGINE': 'xmodule.contentstore.mongo.MongoContentStore',
    'DOC_STORE_CONFIG': {
        'host': 'localhost',
        'db': 'xcontent',
    }
}

DOC_STORE_CONFIG = {
    'host': 'localhost',
    'db': 'test_xmodule',
    'collection': 'test_modulestore',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': TEST_ROOT / 'db' / 'mitx.db'
    },

}

CACHES = {
    # This is the cache used for most things.
    # In staging/prod envs, the sessions also live here.
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mitx_loc_mem_cache',
        'KEY_FUNCTION': 'util.memcache.safe_key',
    },

    # The general cache is what you get if you use our util.cache. It's used for
    # things like caching the course.xml file for different A/B test groups.
    # We set it to be a DummyCache to force reloading of course.xml in dev.
    # In staging environments, we would grab VERSION from data uploaded by the
    # push process.
    'general': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'KEY_PREFIX': 'general',
        'VERSION': 4,
        'KEY_FUNCTION': 'util.memcache.safe_key',
    },

    'mongo_metadata_inheritance': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '/var/tmp/mongo_metadata_inheritance',
        'TIMEOUT': 300,
        'KEY_FUNCTION': 'util.memcache.safe_key',
    }
}

# Dummy secret key for dev
SECRET_KEY = '85920908f28904ed733fe576320db18cabd7b6cd'

# hide ratelimit warnings while running tests
filterwarnings('ignore', message='No request passed to the backend, unable to rate-limit')

################################## OPENID #####################################
MITX_FEATURES['AUTH_USE_OPENID'] = True
MITX_FEATURES['AUTH_USE_OPENID_PROVIDER'] = True

################################## SHIB #######################################
MITX_FEATURES['AUTH_USE_SHIB'] = True
MITX_FEATURES['SHIB_DISABLE_TOS'] = True
MITX_FEATURES['RESTRICT_ENROLL_BY_REG_METHOD'] = True

OPENID_CREATE_USERS = False
OPENID_UPDATE_DETAILS_FROM_SREG = True
OPENID_USE_AS_ADMIN_LOGIN = False
OPENID_PROVIDER_TRUSTED_ROOTS = ['*']

###################### Payment ##############################3
# Enable fake payment processing page
MITX_FEATURES['ENABLE_PAYMENT_FAKE'] = True
# Configure the payment processor to use the fake processing page
# Since both the fake payment page and the shoppingcart app are using
# the same settings, we can generate this randomly and guarantee
# that they are using the same secret.
from random import choice
import string
RANDOM_SHARED_SECRET = ''.join(
    choice(string.letters + string.digits + string.punctuation)
    for x in range(250)
)

CC_PROCESSOR['CyberSource']['SHARED_SECRET'] = RANDOM_SHARED_SECRET
CC_PROCESSOR['CyberSource']['MERCHANT_ID'] = "edx"
CC_PROCESSOR['CyberSource']['SERIAL_NUMBER'] = "0123456789012345678901"
CC_PROCESSOR['CyberSource']['PURCHASE_ENDPOINT'] = "/shoppingcart/payment_fake"

################################# CELERY ######################################

CELERY_ALWAYS_EAGER = True
CELERY_RESULT_BACKEND = 'cache'
BROKER_TRANSPORT = 'memory'

############################ STATIC FILES #############################
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = TEST_ROOT / "uploads"
MEDIA_URL = "/static/uploads/"
STATICFILES_DIRS.append(("uploads", MEDIA_ROOT))

new_staticfiles_dirs = []
# Strip out any static files that aren't in the repository root
# so that the tests can run with only the mitx directory checked out
for static_dir in STATICFILES_DIRS:
    # Handle both tuples and non-tuple directory definitions
    try:
        _, data_dir = static_dir
    except ValueError:
        data_dir = static_dir

    if data_dir.startswith(REPO_ROOT):
        new_staticfiles_dirs.append(static_dir)
STATICFILES_DIRS = new_staticfiles_dirs

FILE_UPLOAD_TEMP_DIR = TEST_ROOT / "uploads"
FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

################### Make tests faster

#http://slacy.com/blog/2012/04/make-your-tests-faster-in-django-1-4/
PASSWORD_HASHERS = (
    # 'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    # 'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    # 'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    # 'django.contrib.auth.hashers.CryptPasswordHasher',
)

################### Make tests quieter

# OpenID spews messages like this to stderr, we don't need to see them:
#   Generated checkid_setup request to http://testserver/openid/provider/login/ with assocication {HMAC-SHA1}{51d49995}{s/kRmA==}

import openid.oidutil
openid.oidutil.log = lambda message, level = 0: None
