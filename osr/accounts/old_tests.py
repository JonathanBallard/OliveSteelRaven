from django.contrib.auth import get_user_model, authenticate, logout, login
from django.test import TestCase
from django.urls import reverse

# Create your tests here.

class LoginTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(username="Tester", password="Pw123456", email="tester@testing.com")
        
        self.signup_url = reverse("account_signup")
        self.login_url = reverse("account_login")
        self.logout_url = reverse("account_logout")
        self.home_url = reverse("accounts:home_page")
        self.account_url = reverse("accounts:account")
    
    #&-----------------------------------------------------------------------------------------------------
    #^ START `Login` Tests
    #&-----------------------------------------------------------------------------------------------------
    def test_user_login_success(self):
        success = self.client.login(username="Tester", password="Pw123456")
        
        self.assertEqual(success, True)
    
    def test_user_login_bad_password(self):
        success = self.client.login(username="Tester", password="someotherstring")
        
        self.assertEqual(success, False)
    
    def test_user_login_bad_username(self):
        success = self.client.login(username="Pinky", password="Pw123456")
        
        self.assertEqual(success, False)
        
    def test_user_login_password_case_mismatch(self):
        success = self.client.login(username="Tester", password="pW123456")
        
        self.assertEqual(success, False)
    
    #&-----------------------------------------------------------------------------------------------------
    #^ START `Signup` Tests
    #&-----------------------------------------------------------------------------------------------------
    
    def test_signup_user_empty_password(self):
        posted_login_data = {"username": "Tester", "password": "", "email": "tester@testing.com"}
        
        resp = self.client.post(self.signup_url, posted_login_data)
        
        self.assertNotEqual(resp.status_code, 200)
    
    def test_signup_user_empty_username(self):
        posted_login_data = {"username": "", "password": "pW123456", "email": "tester@testing.com"}
        
        resp = self.client.post(self.signup_url, posted_login_data)
        
        self.assertNotEqual(resp.status_code, 200)
    
    def test_signup_user_empty_email(self):
        posted_login_data = {"username": "Tester", "password": "pW123456", "email": ""}
        
        resp = self.client.post(self.signup_url, posted_login_data)
        
        self.assertNotEqual(resp.status_code, 200)
    
    def test_signup_user_incomplete_email(self):
        posted_login_data = {"username": "Tester", "password": "pW123456", "email": "pickles@"}
        
        resp = self.client.post(self.signup_url, posted_login_data)
        
        self.assertNotEqual(resp.status_code, 200)
    
    def test_signup_user_incomplete_email_2(self):
        posted_login_data = {"username": "Tester", "password": "pW123456", "email": "pickles@gmail"}      
        resp = self.client.post(self.signup_url, posted_login_data)
        
        self.assertNotEqual(resp.status_code, 200)
    
    def test_signup_user_incomplete_email_3(self):
        posted_login_data = {"username": "Tester", "password": "pW123456", "email": "p@gmail.com"}
        
        resp = self.client.post(self.signup_url, posted_login_data)
        
        self.assertNotEqual(resp.status_code, 200)
        
    #&-----------------------------------------------------------------------------------------------------
    #^ START `Logout` Tests
    #&-----------------------------------------------------------------------------------------------------
    
    def test_logout(self):
        self.client.force_login(self.user)
        
        resp = self.client.post(self.logout_url)
        
        self.assertEqual(resp.url, reverse('accounts:home_page')) #type: ignore
    
    #&-----------------------------------------------------------------------------------------------------
    #^ START `Logout` Tests
    #&-----------------------------------------------------------------------------------------------------
    
    def test_anonymous_account(self):
        resp = self.client.get(self.account_url)
        
        # Shows anonymous user redirected to login
        self.assertEqual(resp.status_code, 302)