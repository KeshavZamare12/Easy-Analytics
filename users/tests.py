# users/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile
import pandas as pd
import json
import io

class UserViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile = Profile.objects.create(user=self.user)

    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'newpass',
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertEqual(response.wsgi_request.user, self.user)

    def test_view_profile_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('view_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_edit_profile_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('edit_profile'), {
            'first_name': 'Updated',
            'last_name': 'User',
            'mobile_no': '1234567890',
            'profile_pic': None  # Adjust based on your requirements
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful edit
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_upload_file_view(self):
        self.client.login(username='testuser', password='testpass')
        csv_data = "Column1,Column2\n1,A\n2,B"
        response = self.client.post(reverse('upload_file'), {
            'file_type': 'csv',
            'file': io.BytesIO(csv_data.encode()),  # Create a bytes buffer
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data')

    def test_modify_data_view(self):
        self.client.login(username='testuser', password='testpass')
        # Simulate uploading data first
        csv_data = "Column1,Column2\n1,A\n2,B\n3,C"
        self.client.post(reverse('upload_file'), {
            'file_type': 'csv',
            'file': io.BytesIO(csv_data.encode()),
        })
        # Now test modifying the data
        response = self.client.post(reverse('modify_data_view'), {
            'action': 'drop_null_rows',
            'selected_columns': ['Column1'],
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'modified_data')

    def test_download_file_view(self):
        self.client.login(username='testuser', password='testpass')
        csv_data = "Column1,Column2\n1,A\n2,B"
        self.client.post(reverse('upload_file'), {
            'file_type': 'csv',
            'file': io.BytesIO(csv_data.encode()),
        })
        response = self.client.get(reverse('download_file'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="modified_data.csv"')

    def test_visualize_data_view(self):
        self.client.login(username='testuser', password='testpass')
        csv_data = "Column1,Column2\n1,A\n2,B\n3,C"
        self.client.post(reverse('upload_file'), {
            'file_type': 'csv',
            'file': io.BytesIO(csv_data.encode()),
        })
        response = self.client.post(reverse('visualize_data'), {
            'column_name': 'Column1',
            'plot_type': 'bar',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'plot_html')

    def tearDown(self):
        self.user.delete()
        self.profile.delete()
