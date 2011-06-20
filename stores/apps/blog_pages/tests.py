"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import datetime
import logging
import time

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from blog_pages.models import *


class PagesTest(TestCase):
    fixtures = [
        'greatcoins_market.json', 
        'greatcoins_subscriptions.json', 
        'greatcoins_auth.json', 
        'greatcoins_shops.json',
        'greatcoins_preferences.json',
        'greatcoins_themes.json'
    ]
    
    
    def setUp(self):
        shop = Shop.objects.all()[0]
        about = About(shop=shop)
        about.save()
        
        Menu.create_default(shop)
        
        home = Home(shop=shop)
        home.save()
        
        page = Page(shop=shop, name="Just a Page", name_link="somewhere", title="This is a page", body="some content here")
        page.save()
        
        self.shop = shop
        self.HTTP_HOST = self.shop.default_dns     
        
    def test_posts(self):
        """
        """
        user = self.shop.admin
        success = self.client.login(username=user.username, password="test")
        self.assertEqual(success, True, "Login failed")
        
        #self.assertEqual(response.status_code, 200)
        #self.assertContains(response, "My Unique Item", count=None, status_code=200, msg_prefix='')
        response = self.client.get(reverse("blog_pages"), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        # Test add new post 
        response = self.client.get(reverse("post_add"), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        posts = Post.objects.filter(shop=self.shop)
        l = len(posts)
        response = self.client.post(reverse("post_add"),{'title': 'Post Title', 'body': "Post body"}, HTTP_HOST=self.HTTP_HOST, follow=True)
        # Check that redirects to blog list
        self.assertContains(response, "Post successfully saved.", count=None, status_code=200, msg_prefix='')
        # Check that there is one more post
        posts = Post.objects.filter(shop=self.shop)
        self.assertEqual(posts.count(), l + 1)
        
        # Test post edition
        post = Post(shop=self.shop, title="Orignal title", body="original body")
        post.save()
        post_id = post.id
        response = self.client.post(reverse("post_edit", args=[post_id]), {'title': 'New Title', 'body': "New body"}, HTTP_HOST=self.HTTP_HOST, follow=True)
        self.assertContains(response, "Post successfully saved.", count=None, status_code=200, msg_prefix='')
        
        # Check that post was really edited
        edited_post = Post.objects.filter(id=post_id)[0]
        self.assertEqual(edited_post.title, "New Title")
        self.assertEqual(edited_post.body, "New body")
        
        # Test post deletion
        self.assertEqual(len(Post.objects.filter(id=post_id)), 1)
        response = self.client.get(reverse("post_delete", args=[post_id]), HTTP_HOST=self.HTTP_HOST, follow=True)
        self.assertEqual(response.status_code, 200)
        # Check that post was deleted
        self.assertEqual(len(Post.objects.filter(id=post_id)), 0)
        
    def test_pages(self):
       
        user = self.shop.admin
        success = self.client.login(username=user.username, password="test")
        self.assertEqual(success, True, "Login failed")
        
        # Home page
        response = self.client.get(reverse("page_edit_home"), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse("page_edit_home"), {'title': 'Welcome to this shop. I just have to change this title', 'body': 'this body chages too!'}, HTTP_HOST=self.HTTP_HOST, follow=True)
        self.assertEqual(response.status_code, 200)
        
        home = Home.objects.filter(shop=self.shop)[0]
        self.assertEqual(home.title,'Welcome to this shop. I just have to change this title')
        
        # About us page        
        response = self.client.get(reverse("page_edit_about"), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse("page_edit_about"), {'title': 'Some about us text', 'body': 'this body chages too!'}, HTTP_HOST=self.HTTP_HOST, follow=True)
        self.assertContains(response, "Page successfully saved.", count=None, status_code=200, msg_prefix='')
        about = About.objects.filter(shop=self.shop)[0]
        self.assertEqual(about.title,'Some about us text')
        
        # New Page        
        response = self.client.get(reverse("page_create"), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)

        total_pages = Page.objects.all().count()        
        response = self.client.post(reverse("page_create"),  {'title': 'A page title', 'name': 'some name', 'name_link': 'some-name-link', 'body': 'this is the page body!'}, HTTP_HOST=self.HTTP_HOST, follow=True)
        self.assertContains(response, "Page successfully saved.", count=None, status_code=200, msg_prefix='')
        new_total_pages = Page.objects.all().count()
        self.assertEqual(new_total_pages, total_pages + 1)
        
        # Edit page
        page = Page.objects.filter(shop=self.shop)[0]
        
        page_id = page.id
        response = self.client.get(reverse("page_edit", args=[page_id]), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse("page_edit", args=[page_id]), {'title': 'This is the new title', 'name': 'some new name', 'name_link': 'some-new-link', 'body': 'this is the new body'}, HTTP_HOST=self.HTTP_HOST, follow=True)
        self.assertContains(response, "Page successfully edited.", count=None, status_code=200, msg_prefix='')
        
        edited_page = Page.objects.filter(id=page_id)[0]
        self.assertEqual(edited_page.title, "This is the new title")
        self.assertEqual(edited_page.name, "some new name")
        self.assertEqual(edited_page.name_link, "some-new-link")
        self.assertEqual(edited_page.body, "this is the new body")
        
        response = self.client.get(reverse("page_delete", args=[page_id]), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(len(Page.objects.filter(id=page_id)), 0)
    
    def test_links(self):

        user = self.shop.admin
        success = self.client.login(username=user.username, password="test")
        self.assertEqual(success, True, "Login failed")
        
        # Links
        response = self.client.get(reverse("navigation"), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        menu = self.shop.menu_set.all()[0]
        
        # Add link
        response = self.client.get(reverse("link_add", args=[menu.id]), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        a_links = Link.objects.all().count()
        response = self.client.post(reverse("link_add", args=[menu.id]), {'name': 'Link name' , 'to': '/home/' , 'title': 'link title'} , HTTP_HOST=self.HTTP_HOST, follow=True)
        
        self.assertContains(response, "Link successfully saved", count=None, status_code=200, msg_prefix='')
        b_links = Link.objects.all().count()
        self.assertEquals(b_links, a_links + 1)
        
        link = Link.objects.all()[0]
        
        # Edit link
        response = self.client.get(reverse("link_edit", args=[link.id]), HTTP_HOST=self.HTTP_HOST)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse("link_edit", args=[link.id]), {'name': 'Link name' , 'to': '/home/' , 'title': 'link title'} , HTTP_HOST=self.HTTP_HOST, follow=True)
        self.assertContains(response, "Link successfully edited", count=None, status_code=200, msg_prefix='')
        
        # Delete link
        response = self.client.get(reverse("link_delete", args=[link.id]), HTTP_HOST=self.HTTP_HOST, follow=True)
        self.assertContains(response, "Link successfully deleted", count=None, status_code=200, msg_prefix='')

        
#        response = self.client.get(reverse("link_order"), HTTP_HOST=self.HTTP_HOST)
#        self.assertEqual(response.status_code, 200)
        
        
        
        
        