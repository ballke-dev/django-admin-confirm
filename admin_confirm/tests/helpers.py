import socket

from django.core.cache import cache
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from tests.test_project.settings import SELENIUM_HOST

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By


class AdminConfirmTestCase(TestCase):
    """
    Helper TestCase class and common associated assertions
    """

    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username="super", email="super@email.org", password="pass"
        )

    def setUp(self):
        cache.clear()
        self.client.force_login(self.superuser)
        self.factory = RequestFactory()

    def _assertManyToManyFormHtml(self, rendered_content, options, selected_ids):
        # Form data should be embedded and hidden on confirmation page
        # Should have the correct ManyToMany options selected
        for option in options:
            self.assertIn(
                f'<option value="{option.id}"{" selected" if option.id in selected_ids else ""}>{str(option)}</option>',
                rendered_content,
            )
        # ManyToManyField should be embedded
        self.assertIn("related-widget-wrapper", rendered_content)

    def _assertSubmitHtml(
        self, rendered_content, save_action="_save", multipart_form=False
    ):
        # Submit should conserve the save action
        self.assertIn(
            f'<input type="submit" value="Sim, tenho certeza" name="{save_action}">',
            rendered_content,
        )
        # There should not be _confirm_add or _confirm_change sent in the form on confirmaiton page
        self.assertNotIn("_confirm_add", rendered_content)
        self.assertNotIn("_confirm_change", rendered_content)

        confirmation_received_html = (
            '<input type="hidden" name="_confirmation_received" value="True">'
        )

        if multipart_form:
            # Should have _confirmation_received as a hidden field
            self.assertIn(confirmation_received_html, rendered_content)
        else:
            self.assertNotIn(confirmation_received_html, rendered_content)

    def _assertSimpleFieldFormHtml(self, rendered_content, fields):
        for k, v in fields.items():
            self.assertIn(f'name="{k}"', rendered_content)
            self.assertIn(f'value="{v}"', rendered_content)

    def _assertFormsetsFormHtml(self, rendered_content, inlines):
        for inline in inlines:
            for field in inline.fields:
                self.assertIn("apple", rendered_content)


class AdminConfirmIntegrationTestCase(LiveServerTestCase):
    # Setup/Teardown Methods
    @classmethod
    def setUpClass(cls):
        cls.host = socket.gethostbyname(socket.gethostname())
        cls.selenium = webdriver.Remote(
            command_executor=f"http://{SELENIUM_HOST}:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.FIREFOX,
        )
        super().setUpClass()

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="super", email="super@email.org", password="pass"
        )
        self.client.force_login(self.superuser)

        cookie = self.client.cookies["sessionid"]
        self.selenium.get(
            self.live_server_url + "/admin/"
        )  # selenium will set cookie domain based on current page domain
        self.selenium.add_cookie(
            {"name": "sessionid", "value": cookie.value, "secure": False, "path": "/"}
        )
        return super().setUp()

    def tearDown(self):
        cache.clear()
        self.selenium.get(self.live_server_url)
        return super().tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    # Helper Methods

    def set_value(self, by, by_value, value):
        element = self.selenium.find_element(by, by_value)
        element.clear()
        element.send_keys(value)

    def select_value(self, by, by_value, value):
        element = Select(self.selenium.find_element(by, by_value))
        element.select_by_value(value)

    def select_index(self, by, by_value, index):
        element = Select(self.selenium.find_element(by, by_value))
        element.select_by_index(index)

    def print_hidden_form(self):
        hidden_form = self.selenium.find_element(By.ID, "hidden-form")
        print(hidden_form.get_attribute("innerHTML"))
