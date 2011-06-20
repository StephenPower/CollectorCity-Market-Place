from auth.tests.basic import BASIC_TESTS
#from auth.tests.views import PasswordResetTest, ChangePasswordTest, LoginTest, LogoutTest
from auth.tests.forms import FORM_TESTS
from auth.tests.tokens import TOKEN_GENERATOR_TESTS

# The password for the fixture data users is 'password'

__test__ = {
    'BASIC_TESTS': BASIC_TESTS,
    'FORM_TESTS': FORM_TESTS,
    'TOKEN_GENERATOR_TESTS': TOKEN_GENERATOR_TESTS,
}
