import unittest

from auth.models import User

class CoreTest(unittest.TestCase):
    def setUp(self):
        self.user = User(username="core_tester",
                         first_name="first",
                         last_name="last", 
                         email="tester@test.com")
        self.user.set_password("test")
        self.user.save()
    
    def tearDown(self):
        self.user.delete()
        
    def test_email_backend(self):
        #from django.contrib.auth import login
        request =  object()
        request.POST = {'username': 'core_tester',
                        'password': 'test'}
        
        from auth import login
        login(request, self.user)
        
    

    