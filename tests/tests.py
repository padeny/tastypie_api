import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from tastypie.test import ResourceTestCaseMixin

from tastypie_api import http
from tests.models import Entry


class EntryResourceTest(ResourceTestCaseMixin, TestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['test_entries.json']

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        # Create a user.
        self.username = 'daniel'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'daniel@example.com', self.password)

        # Fetch the ``Entry`` object we'll use in testing.
        # Note that we aren't using PKs because they can change depending
        # on what other tests are running.
        self.entry_1 = Entry.objects.get(slug='first-post')

        # We also build a detail URI, since we will be using it all over.
        # DRY, baby. DRY.
        self.detail_url = '/api/v1/entries/{0}/'.format(self.entry_1.pk)

        # The data we'll send on POST requests. Again, because we'll use it
        # frequently (enough).
        self.post_data = {
            'user': '/api/v1/user/{0}/'.format(self.user.pk),
            'title': 'Sixth Post!',
            'slug': 'sixth-post',
            'created': '2012-05-01T22:05:12'
        }

    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    def assertValidCustomeResponse(self, resp):
        " validate response format"
        self.assertValidJSONResponse(resp)
        self.assertKeys(self.deserialize(resp), ['status_code', 'msg', 'meta', 'data'])

    def assertSuccessResponse(self, resp):
        self.assertEqual(self.deserialize(resp)['status_code'], http.SUCCESS)

    def assertResponseStatusCode(self, resp, status_code):
        self.assertEqual(self.deserialize(resp)['status_code'], status_code)

    def assertHttpUnauthorized(self, resp):
        self.assertEqual(self.deserialize(resp)['status_code'], http.HttpUnauthorized.res_code)

    def test_get_list_unauthenticated(self):
        resp = self.api_client.get('/api/v1/entries/', format='json')
        self.assertValidCustomeResponse(resp)
        self.assertHttpUnauthorized(resp)

    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/entries/', format='json', authentication=self.get_credentials())
        self.assertValidCustomeResponse(resp)
        # Scope out the data for correctness.
        self.assertEqual(len(self.deserialize(resp)['data']), 5)

    def test_get_detail_unauthenticated(self):
        resp = self.api_client.get(self.detail_url, format='json')
        self.assertValidCustomeResponse(resp)
        self.assertHttpUnauthorized(resp)

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials())
        self.assertValidCustomeResponse(resp)
        # We use ``assertKeys`` here to just verify the keys, not all the data.
        self.assertKeys(self.deserialize(resp)['data'], ['created', 'slug', 'title', 'user', 'image'])
        self.assertEqual(self.deserialize(resp)['data']['title'], 'First Post!')

    def test_post_list_unauthenticated(self):
        resp = self.api_client.post('/api/v1/entries/', format='json', data=self.post_data)
        self.assertValidCustomeResponse(resp)
        self.assertHttpUnauthorized(resp)

    def test_post_list(self):
        # Check how many are there first.
        self.assertEqual(Entry.objects.count(), 5)
        resp = self.api_client.post(
            '/api/v1/entries/', format='json', data=self.post_data, authentication=self.get_credentials())
        self.assertSuccessResponse(resp)
        # Verify a new one has been added.
        self.assertEqual(Entry.objects.count(), 6)

    def test_post_form_data(self):
        # Check how many are there first.
        image = SimpleUploadedFile("12.png", b"file_content")
        post_form_data = {"image": image, "created": "2012-05-01T20:06:12", "title": "sasa", "slug": "test"}
        resp = self.api_client.post(
            '/api/v1/entries/', data=post_form_data, format='json', authentication=self.get_credentials())
        self.deserialize(resp)
        self.assertSuccessResponse(resp)
        # Verify a new one has been added.
        self.assertEqual(Entry.objects.count(), 6)
        yy = Entry.objects.get(id=6)
        self.assertEqual(yy.image.name, image.name)

    def test_patch_detail_form_data(self):
        # Check how many are there first.
        self.assertEqual(Entry.objects.count(), 5)
        image = SimpleUploadedFile("12.png", b"file_content")
        patch_form_data = {"image": image, "created": "2012-05-01T20:06:12", " slug": "test"}
        resp = self.api_client.patch('/api/v1/entries/2/', data=patch_form_data, authentication=self.get_credentials())
        self.deserialize(resp)
        self.assertSuccessResponse(resp)
        # Verify a new one has been added.
        self.assertEqual(Entry.objects.count(), 5)
        yy = Entry.objects.get(id=2)
        self.assertEqual(yy.image.name, image.name)
        self.assertEqual(yy.title, "Second Post!")

    def test_put_detail_form_data(self):
        # Check how many are there first.
        self.assertEqual(Entry.objects.count(), 5)
        image = SimpleUploadedFile("12.png", b"file_content")
        put_form_data = {"image": image, "created": "2012-05-01T20:06:12", "title": "sasa"}
        resp = self.api_client.put(
            '/api/v1/entries/2/', data=put_form_data, authentication=self.get_credentials())
        self.deserialize(resp)
        self.assertSuccessResponse(resp)
        # Verify a new one has been added.
        self.assertEqual(Entry.objects.count(), 5)
        yy = Entry.objects.get(id=2)
        self.assertEqual(yy.image.name, image.name)

    def test_put_detail_unauthenticated(self):
        resp = self.api_client.put(self.detail_url, format='json', data={})
        self.assertValidCustomeResponse(resp)
        self.assertHttpUnauthorized(resp)

    def test_put_detail(self):
        # Grab the current data & modify it slightly.
        original_data = self.deserialize(
            self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials()))
        new_data = original_data.copy()
        new_data['title'] = 'Updated: First Post'
        new_data['created'] = '2012-05-01T20:06:12'
        self.assertEqual(Entry.objects.count(), 5)
        resp = self.api_client.put(self.detail_url, format='json', data=new_data, authentication=self.get_credentials())
        self.assertValidCustomeResponse(resp)
        self.assertResponseStatusCode(resp, http.HttpAccepted.res_code)
        # Make sure the count hasn't changed & we did an update.
        self.assertEqual(Entry.objects.count(), 5)
        # Check for updated data.
        detail_pk = self.entry_1.pk
        self.assertEqual(Entry.objects.get(pk=detail_pk).title, 'Updated: First Post')
        self.assertEqual(Entry.objects.get(pk=detail_pk).slug, 'first-post')
        self.assertEqual(Entry.objects.get(pk=detail_pk).created, datetime.datetime(2012, 5, 1, 20, 6, 12))

    def test_delete_detail_unauthenticated(self):
        resp = self.api_client.delete(self.detail_url, format='json')
        self.assertValidCustomeResponse(resp)
        self.assertHttpUnauthorized(resp)

    def test_delete_detail(self):
        self.assertEqual(Entry.objects.count(), 5)
        resp = self.api_client.delete(self.detail_url, format='json', authentication=self.get_credentials())
        self.assertValidCustomeResponse(resp)
        self.assertResponseStatusCode(resp, http.HttpAccepted.res_code)
        self.assertEqual(Entry.objects.count(), 4)

    def test_paginator(self):
        resp = self.api_client.get(
            '/api/v1/entries/?limit=2&page_num=1', format='json', authentication=self.get_credentials())
        self.assertValidCustomeResponse(resp)
        # Scope out the data for correctness.
        self.assertEqual(len(self.deserialize(resp)['data']), 2)
        self.assertEqual(self.deserialize(resp)['meta']['previous'], None)

        resp1 = self.api_client.get(
            '/api/v1/entries/?limit=0&page_num=1', format='json', authentication=self.get_credentials())
        self.assertValidCustomeResponse(resp1)
        # Scope out the data for correctness.
        self.assertEqual(len(self.deserialize(resp1)['data']), 5)
        self.assertEqual(self.deserialize(resp1)['meta']['previous'], None)

    def test_paginator_exception(self):
        resp1 = self.api_client.get(
            '/api/v1/entries/?limit=2&page_num=aa', format='json', authentication=self.get_credentials())
        resp2 = self.api_client.get(
            '/api/v1/entries/?limit=2&page_num=-1', format='json', authentication=self.get_credentials())
        self.assertValidCustomeResponse(resp1)
        self.assertResponseStatusCode(resp1, http.FAILED)
        self.assertValidCustomeResponse(resp2)
        self.assertResponseStatusCode(resp2, http.FAILED)

    def test_custom_api_unauthenticated(self):
        resp1 = self.api_client.get('/api/v1/entries/test_custom_api/', format='json')
        self.assertValidCustomeResponse(resp1)
        self.assertHttpUnauthorized(resp1)

        resp2 = self.api_client.get('/api/v1/entries/test_custom_api2/', format='json')
        self.assertValidCustomeResponse(resp2)
        self.assertSuccessResponse(resp2)

        resp3 = self.api_client.get('/api/v1/entries/test_custom_api3/', format='json')
        self.assertValidCustomeResponse(resp3)
        self.assertSuccessResponse(resp3)

        resp4 = self.api_client.get('/api/v1/entries/test_custom_api4/', format='json')
        self.assertValidCustomeResponse(resp4)
        self.assertSuccessResponse(resp4)

    def test_custom_api_request_method(self):
        resp2 = self.api_client.post('/api/v1/entries/test_custom_api2/', format='json')
        self.assertValidCustomeResponse(resp2)
        self.assertResponseStatusCode(resp2, http.HttpMethodNotAllowed.res_code)

        resp3 = self.api_client.post('/api/v1/entries/test_custom_api3/', format='json')
        self.assertValidCustomeResponse(resp3)
        self.assertSuccessResponse(resp3)


class Entry2ResourceTest(ResourceTestCaseMixin, TestCase):
    """
        SessionAuthentication的单元测试, 每个测试方法中先调用下self.setup_session()即可
    """
    fixtures = ['test_entries.json']

    def setUp(self):
        super(Entry2ResourceTest, self).setUp()

        # Create a user.
        self.username = 'daniel'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'daniel@example.com', self.password)

        # Fetch the ``Entry`` object we'll use in testing.
        # Note that we aren't using PKs because they can change depending
        # on what other tests are running.
        self.entry_1 = Entry.objects.get(slug='first-post')

        # We also build a detail URI, since we will be using it all over.
        # DRY, baby. DRY.
        self.detail_url = '/api/v1/entries2/{0}/'.format(self.entry_1.pk)

        # The data we'll send on POST requests. Again, because we'll use it
        # frequently (enough).
        self.post_data = {
            'user': '/api/v1/user/{0}/'.format(self.user.pk),
            'title': 'Sixth Post!',
            'slug': 'sixth-post',
            'created': '2012-05-01T22:05:12'
        }

    def setup_session(self):
        self.api_client.client.login(username=self.username, password=self.password)

    def assertValidCustomeResponse(self, resp):
        " validate response format"
        self.assertValidJSONResponse(resp)
        self.assertKeys(self.deserialize(resp), ['status_code', 'msg', 'meta', 'data'])

    def assertSuccessResponse(self, resp):
        self.assertEqual(self.deserialize(resp)['status_code'], http.SUCCESS)

    def assertResponseStatusCode(self, resp, status_code):
        self.assertEqual(self.deserialize(resp)['status_code'], status_code)

    def assertHttpUnauthorized(self, resp):
        self.assertEqual(self.deserialize(resp)['status_code'], http.HttpUnauthorized.res_code)

    def test_get_list_unauthenticated(self):
        resp = self.api_client.get('/api/v1/entries2/', format='json')
        self.assertValidCustomeResponse(resp)
        self.assertHttpUnauthorized(resp)

    def test_get_list_json(self):
        self.setup_session()

        resp = self.api_client.get('/api/v1/entries2/', format='json')
        self.assertValidCustomeResponse(resp)
        # Scope out the data for correctness.
        self.assertEqual(len(self.deserialize(resp)['data']), 5)

    def test_get_detail_unauthenticated(self):
        resp = self.api_client.get(self.detail_url, format='json')
        self.assertValidCustomeResponse(resp)
        self.assertHttpUnauthorized(resp)

    def test_get_detail_json(self):
        self.setup_session()

        resp = self.api_client.get(self.detail_url, format='json')
        self.assertValidCustomeResponse(resp)
        # We use ``assertKeys`` here to just verify the keys, not all the data.
        self.assertKeys(self.deserialize(resp)['data'], ['created', 'slug', 'title', 'user', 'image'])
        self.assertEqual(self.deserialize(resp)['data']['title'], 'First Post!')

    def test_post_list_unauthenticated(self):
        resp = self.api_client.post('/api/v1/entries2/', format='json', data=self.post_data)
        self.assertValidCustomeResponse(resp)
        self.assertHttpUnauthorized(resp)

    def test_post_list(self):
        self.setup_session()

        # Check how many are there first.
        self.assertEqual(Entry.objects.count(), 5)
        resp = self.api_client.post(
            '/api/v1/entries2/', format='json', data=self.post_data)
        self.assertSuccessResponse(resp)
        # Verify a new one has been added.
        self.assertEqual(Entry.objects.count(), 6)
