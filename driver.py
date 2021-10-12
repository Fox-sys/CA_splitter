import os
import time
import random
import datetime


from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


class BaseDriver(webdriver.Chrome):
    page_info_path: str = ''  # директория для сохранения информации о странице

    def __init__(self, default=False, agent=None, cookie_saver=None, window_size="1920,1080"):

        self.default = default
        self.cookie_saver = cookie_saver

        # General options
        # chrome_options = Options()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--window-size=%s" % window_size)
        chrome_options.add_experimental_option("prefs",
                                               {"profile.default_content_setting_values.notifications": 2})

        # Headless options
        self.just_browser = False

        # chrome_options.add_argument('--user-data-dir=~/.config/google-chrome')


        #   2. Delay initialization

        super(BaseDriver, self).__init__(executable_path=ChromeDriverManager().install(),
                                         options=chrome_options,
                                         service_log_path='')

    def save_page_info(self, file_prefix: str = '', img: bool = True, html: bool = True, ):
        if file_prefix:
            file_prefix += '_'

        directory_name = datetime.datetime.utcnow().strftime("%d%m%Y-%H%M%S")

        if not os.path.exists(self.page_info_path):
            os.mkdir(self.page_info_path)

        directory_path = f'{self.page_info_path}/{directory_name}'
        try:
            os.mkdir(directory_path)
        except FileExistsError:
            pass

        save_img_success = False
        if img:
            save_img_success = self.save_screenshot(f'{directory_path}/{file_prefix}screen.png')

        save_html_success = False
        if html:
            try:
                with open(f'{directory_path}/{file_prefix}page_source.html', 'w', encoding='utf-8') as f:
                    f.write(self.page_source)
                    save_html_success = True
            except:
                pass


    @staticmethod
    def delay_till_shift(account, immediately=False):
        if immediately:
            return 0
        shift_table = {
            1: 3,
            2: 9,
            3: 15,
            4: 21
        }

        print(account)
        start_hour = shift_table[account.shift]

        time_now = list(map(int, str(datetime.datetime.utcnow()).split(" ")[1].split(".")[0].split(":")))
        is_hour_overlap = False
        if time_now[0] > start_hour:
            is_hour_overlap = True
        start_seconds = start_hour * 60 * 60
        if is_hour_overlap:
            start_seconds += 60 * 60 * 24
        seconds_now = (time_now[0] * 60 + time_now[1]) * 60 + time_now[2]
        sleep_time = int(start_seconds - seconds_now)
        print(
            f"will start in {sleep_time // 60 // 60}h {sleep_time // 60 % 60}min, now {(time_now[0] + 3) % 24}:{str(datetime.datetime.utcnow()).split(' ')[1].split('.')[0][3:-3]} MSK")
        # print(f"start at {int((time_now[0] + sleep_time//60//60 + (time_now[1] + sleep_time//60%60)//60 + 3) % 24)}:{int((time_now[1] + sleep_time//60%60) % 60)}")
        return sleep_time

    def __del__(self):
        try:
            self.quit()
        except:
            pass

    # Tools

    def close_tab_save_ram(self):
        self.execute_script("window.open('');")
        self.close()
        self.switch_to.window(self.window_handles[-1])

    def elms(self, css, father=None):
        if father is None:
            father = self
        return father.find_elements_by_css_selector(css)

    def elm(self, css, father=None):
        if father is None:
            father = self
        if self.has_element(css, father):
            return self.elms(css, father)[0]
        return None

    def has_element(self, css, father=None):
        if father is None:
            father = self
        elms = self.elms(css, father)
        return len(elms) > 0

    def get_text(self, css, father=None):
        if father is None:
            father = self
        if self.has_element(css, father):
            return self.elms(css, father)[0].text
        return ""

    def get_attribute(self, css, attr, father=None):
        if father is None:
            father = self
        if self.has_element(css, father):
            return self.elms(css, father)[0].get_attribute(attr)
        return ""

    def hover_elm(self, elm):
        self.execute_script("arguments[0].scrollIntoView();", elm)
        actions = ActionChains(self)
        actions.move_to_element(elm).perform()

    def smart_click(self, css, father=None):
        if father is None:
            father = self
        if self.has_element(css, father):
            elm = self.elm(css)
            self.execute_script("arguments[0].scrollIntoView();", elm)
            actions = ActionChains(self)
            actions.move_to_element(elm).click().perform()
        else:
            print("No such element to smart_click: ", css)

    def click(self, css, father=None):
        if father is None:
            father = self
        if self.has_element(css, father):
            self.elms(css, father)[0].click()
        else:
            print("No such element to click: ", css)

    def input_text_slow(self, css, MESSAGE):
        def slow_spelling(elm, text):
            def hit_key(elm, char):
                time.sleep(random.uniform(0.01, 0.1))
                elm.send_keys(char)

            text = str(text)
            for c in text:
                hit_key(elm, c)
            return

        elm = self.elm(css)
        try:
            elm.clear()
        except Exception as e:
            pass

        slow_spelling(elm, MESSAGE)

    def input_text(self, css, text):
        elm = self.elm(css)
        self.strong_click(css)
        elm.clear()
        elm.send_keys(str(text))

    def wait_for(self, css, timeout=10):
        try:
            WebDriverWait(self,
                          timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
            return True
        except TimeoutException:
            print(f'Tools.wait_for: failed to wait element {css} on: {self.current_url}')
            return False

    def scroll_down_fast(self):
        height = self.execute_script("return document.body.scrollHeight")
        scheight = .1
        while scheight < 9.9999:
            scroll_to = height - height / scheight
            self.execute_script("window.scrollTo(0, %s);" % scroll_to)
            scheight += random.uniform(0.01, 1)
        time.sleep(random.uniform(1, 2))

        self.scroll_all_down()

    def scroll_down(self):
        height = self.execute_script("return document.body.scrollHeight")
        scheight = .1
        while scheight < 9.9999:
            scroll_to = height - height / scheight
            self.execute_script("window.scrollTo(0, %s);" % scroll_to)
            scheight += random.uniform(0.001, 0.01)
        time.sleep(random.uniform(1, 2))

    def scroll_up(self):
        height = self.execute_script("return document.body.scrollHeight")
        scheight = .1
        while scheight < 9.9999:
            scroll_to = height / scheight
            self.execute_script("window.scrollTo(0, %s);" % scroll_to)
            scheight += random.uniform(0.001, 0.01)

        time.sleep(random.uniform(1, 2))

    def strong_click(self, css, father=None):
        if father is None:
            father = self
        if self.has_element(css, father):
            elm = self.elm(css, father)
            self.execute_script("arguments[0].click();", elm)
            return True
        else:
            return False

    def scroll_all_up(self):
        self.execute_script("window.scrollTo(0, %s);" % 0)
        time.sleep(random.uniform(1, 2))

    def scroll_all_down(self):
        height = self.execute_script("return document.body.scrollHeight")
        self.execute_script("window.scrollTo(0, %s);" % height)
        time.sleep(random.uniform(1, 2))

    def scroll_up_by(self, x):
        cur_pos = self.execute_script("return window.pageYOffset;")
        self.execute_script(f"window.scrollTo(0, {cur_pos - x});")

    def waiting_for_element_text_to_change(self, css, max_wait_seconds: float = 5,
                                           waiting_step_seconds: float = 0.2) -> bool:
        """
        Ожидание изменения текста элемента.
        Если текст изменился в течении max_wait_seconds, то возвращается True, иначе False.
        """
        waited_seconds = 0
        old_element_text = self.get_text(css)
        while waited_seconds != max_wait_seconds:
            time.sleep(waiting_step_seconds)
            waited_seconds += waiting_step_seconds
            new_element_text = self.get_text(css)
            if old_element_text != new_element_text:
                return True
        return False
