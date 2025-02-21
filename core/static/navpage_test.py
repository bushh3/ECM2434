from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.urls import reverse
import time

class JSInteractionTests(TestCase):
    def setUp(self):
        # Setup for the browser driver
        self.driver = webdriver.Chrome(executable_path='/path/to/chromedriver')  # Replace with your ChromeDriver path
        self.url = reverse('core:login')  # Login page URL defined in your Django app

    def tearDown(self):
        # Close the browser after the test
        self.driver.quit()

    def test_set_active_function(self):
        # Load the login page
        self.driver.get(f'http://localhost:8000{self.url}')
        time.sleep(1)  # Wait for the page to load

        # Get the item elements
        items = self.driver.find_elements(By.CSS_SELECTOR, ".item")
        assert len(items) > 0, "Item elements are not present on the page"

        # Click the first item
        items[0].click()
        time.sleep(0.5)  # Wait for 500ms

        # Ensure the first item is active
        assert 'active' in items[0].get_attribute('class'), "The first item is not active"

        # Ensure the second item is not active
        assert 'active' not in items[1].get_attribute('class'), "The second item should not be active"

        # Ensure the info icon is enabled after activation
        info_icons = items[0].find_elements(By.CSS_SELECTOR, '.info-icon')
        for icon in info_icons:
            assert 'disabled' not in icon.get_attribute('class'), "Info icon should not be disabled after activation"
    
    def test_fetch_user_info(self):
        # Simulate loading the page and fetching user info
        self.driver.get(f'http://localhost:8000{self.url}')
        time.sleep(1)

        # Check if the user score and rank are displayed
        score_element = self.driver.find_element(By.ID, "user-score")
        rank_element = self.driver.find_element(By.ID, "user-rank")

        # Simulate successful API response (this part requires mock data or actual backend response)
        assert score_element.text != "", "User score not loaded"
        assert rank_element.text != "", "User rank not loaded"

    def test_modal_functionality(self):
        # Test the modal open/close functionality
        self.driver.get(f'http://localhost:8000{self.url}')
        time.sleep(1)

        # Find the open modal button and click it
        open_modal_button = self.driver.find_element(By.CSS_SELECTOR, "[onclick*='openModal']")
        open_modal_button.click()
        time.sleep(1)

        # Ensure the modal is displayed after clicking the button
        modal = self.driver.find_element(By.CSS_SELECTOR, ".modal")
        assert modal.is_displayed(), "Modal should be displayed after clicking the button"

        # Find the close button and click it to close the modal
        close_button = modal.find_element(By.CSS_SELECTOR, ".close")
        close_button.click()
        time.sleep(1)

        # Ensure the modal is hidden after clicking the close button
        assert not modal.is_displayed(), "Modal should be hidden after clicking the close button"
