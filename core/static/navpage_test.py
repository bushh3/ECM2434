from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from django.urls import reverse

class JSInteractionTests(TestCase):
    def setUp(self):
        # 设置浏览器驱动
        self.driver = webdriver.Chrome(executable_path='/path/to/chromedriver')  # 请替换为你的 ChromeDriver 路径
        self.url = reverse('core:login')  # 这里根据实际的 URL 修改，假设是登录页面

    def tearDown(self):
        # 测试完成后关闭浏览器
        self.driver.quit()

    def test_set_active_function(self):
        # 加载页面
        self.driver.get(f'http://localhost:8000{self.url}')
        time.sleep(1)  # 等待页面加载

        # 获取所有 .item 元素
        items = self.driver.find_elements(By.CSS_SELECTOR, ".item")
        assert len(items) > 0, "Item elements are not present on the page"

        # 点击第一个 item
        items[0].click()
        time.sleep(0.5)  # 等待 500ms，确保 setActive 被触发

        # 确保第一个 item 被激活
        assert 'active' in items[0].get_attribute('class'), "The first item is not active"

        # 确保第二个 item 没有激活
        assert 'active' not in items[1].get_attribute('class'), "The second item should not be active"

        # 确保点击后的问号被启用
        info_icons = items[0].find_elements(By.CSS_SELECTOR, '.info-icon')
        for icon in info_icons:
            assert 'disabled' not in icon.get_attribute('class'), "Info icon should not be disabled after activation"

    def test_fetch_user_info(self):
        # 模拟点击一个 "info" 按钮，验证排行榜加载
        self.driver.get(f'http://localhost:8000{self.url}')
        time.sleep(1)

        # 假设页面显示了用户积分
        score_element = self.driver.find_element(By.ID, "user-score")
        rank_element = self.driver.find_element(By.ID, "user-rank")

        # 模拟 API 响应
        # (通常这需要通过后端模拟或使用 mock 来提供假数据)
        assert score_element.text != "", "User score not loaded"
        assert rank_element.text != "", "User rank not loaded"

    def test_modal_functionality(self):
        # 测试弹窗的打开和关闭
        self.driver.get(f'http://localhost:8000{self.url}')
        time.sleep(1)

        # 获取第一个包含 "openModal" 的按钮
        open_modal_button = self.driver.find_element(By.CSS_SELECTOR, "[onclick*='openModal']")
        open_modal_button.click()
        time.sleep(1)

        # 确保弹窗显示
        modal = self.driver.find_element(By.CSS_SELECTOR, ".modal")
        assert modal.is_displayed(), "Modal should be displayed after clicking the open button"

        # 关闭弹窗
        close_button = modal.find_element(By.CSS_SELECTOR, ".close")
        close_button.click()
        time.sleep(1)

        # 确保弹窗关闭
        assert not modal.is_displayed(), "Modal should be hidden after clicking the close button"

    def test_modal_prevent_disabled_open(self):
        # 测试禁用状态下点击问号不能打开弹窗
        self.driver.get(f'http://localhost:8000{self.url}')
        time.sleep(1)

        # 获取一个禁用状态的问号图标
        icon = self.driver.find_element(By.CSS_SELECTOR, '.info-icon.disabled')
        
        # 获取点击弹窗的按钮
        open_modal_button = icon.find_element(By.XPATH, './ancestor::button')  # 获取点击弹窗的按钮
        open_modal_button.click()
        time.sleep(1)

        # 确保弹窗没有打开
        modal = self.driver.find_element(By.CSS_SELECTOR, ".modal")
        assert not modal.is_displayed(), "Modal should not open when the icon is disabled"
