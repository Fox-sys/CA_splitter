import time

from driver import BaseDriver

with open('result.txt', 'w') as file:
    file.close()

DAY = 'c%5Bbday%5D={day}&'
MONTH = 'c%5Bbmonth%5D={month}&'
LINK = 'https://vk.com/search?{day}{month}c%5Bcompany%5D={company}&c%5Bname%5D=1&c%5Bper_page%5D=40&c%5Bphoto%5D=0&c%5Bsection%5D=people&c%5Bsex%5D={sex}'


def login(driver, login_vk, password_vk):
    """
    Функция логина
    """
    elements_css = {
        'login': 'input[id="index_email"]',
        'login_pass': 'input[id="index_pass"]',
        'login_button': 'button[id="index_login_button"]',
        'message_input': 'div[id="im_editable{peer_id}"]',
        'message_send_button': 'button.im-chat-input--send',
        'message_text': 'div.im-mess--text',
        'account_messages': 'li.im-mess_out',
        'all_messages': 'li.im-mess',
        'msg_error': 'div.error',
        'top_profile_link': '#top_profile_link',
        'box_body': '.box_body',
        'limit_error': 'div.im-page--error--visible'
    }
    driver.get('https://vk.com')
    driver.input_text_slow(elements_css['login'], login_vk)
    driver.input_text_slow(elements_css['login_pass'], password_vk)
    driver.click(elements_css['login_button'])


def check_link(link, login_vk, password_vk):
    driver = BaseDriver()
    time.sleep(1)
    login(driver, login_vk, password_vk)
    time.sleep(1)
    driver.get(link)
    time.sleep(1)
    elm = driver.elm('span.page_block_header_count')
    amount = int(elm.text.replace(',', '').replace(' ', ''))
    return link, amount


def split_link(link, amount):
    with open('result.txt', 'a') as file:
        if amount <= 1000:
            file.write(link)
        elif 1000 < amount <= 2000:
            [file.write(LINK.format(day='', month='', sex=i, company=company) + '\n') for i in range(1, 3)]
        elif 2000 < amount <= 12000:
            [file.write(LINK.format(day='', month=MONTH.format(month=i), sex=0, company=company) + '\n') for i in
             range(1, 13)]
        elif 12000 < amount <= 30000:
            [file.write(LINK.format(day=DAY.format(day=i), month='', sex=0, company=company) + '\n') for i in
             range(1, 32)]
        elif 30000 < amount <= 60000:
            for i in range(1, 32):
                for j in 1, 2:
                    file.write(LINK.format(day=DAY.format(day=i), month='', sex=j, company=company) + '\n')
        else:
            for i in range(1, 32):
                for j in range(1, 13):
                    for x in 1, 2:
                        file.write(LINK.format(
                            day=DAY.format(day=i),
                            month=MONTH.format(month=j),
                            sex=x,
                            company=company) + '\n')
        file.close()


if __name__ == '__main__':
    login_vk = input('Введите логин от вк: ')
    password_vk = input('Введите пароль от вк: ')
    company = input('Введите место работы: ')
    link = LINK.format(day='', month='', sex=0, company=company)
    info = check_link(link, login_vk, password_vk)
    split_link(*info)
