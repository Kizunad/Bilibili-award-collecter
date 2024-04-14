""" imports """
from DrissionPage import ChromiumPage,ChromiumOptions
import time


""" CONSTANTS """
WINDOWSIZE_X = 1100
WINDOWSIZE_Y = 958


"""Public variables"""
#Str
cookies = ''
csrf = ''
id = ''



""" functions """
#main
def main():
    init()
    page_actions(url=exchange_url)
    listen_for_cookies()
    if(WaitUntilCanCollectAward()):
        CollectAward()
        print_dhm()


#init
def init():
    """ public variables"""
    global page,init_file
    img_file_path = './images'
    detect_file(img_file_path)
    init_file = './init.txt'
    detect_txt_file(init_file)
    init_file_read()
    co  =ChromiumOptions().set_browser_path(web_path)
    """ 初始化浏览器 """
    page = ChromiumPage(co)
    page.set.window.size(WINDOWSIZE_X,WINDOWSIZE_Y)
    print('[INFO] Browser initialized,please dont change the window size.')
    
    
    
def init_file_read():
    global web_path,exchange_url,API_username,API_password
    with open(init_file, 'r') as f:
        init_data = f.read().split('\n')
    if len(init_data)!=4:
        print('[INFO] init.txt is empty')
        with open(init_file, 'w') as f:
            web_path = input("请输入可执行浏览器路径：\n")
            f.write(web_path+'\n')
            print(f"[INFO] {web_path} saved to init.txt")
            exchange_url = input("请输入b站兑换码网址：\n")
            f.write(exchange_url+'\n')
            print(f"[INFO] {exchange_url} saved to init.txt")
            API_username = input("请输入文本识别账号：\n")
            f.write(API_username+'\n')
            print(f"[INFO] {API_username} saved to init.txt")
            API_password = input("请输入文本识别密码：\n")
            f.write(API_password+'\n')
            print(f"[INFO] {API_password} saved to init.txt")
    else:
        web_path = init_data[0]
        exchange_url = init_data[1]
        API_username = init_data[2]
        API_password = init_data[3]
        print(f"[INFO] web_path: {web_path}, exchange_url: {exchange_url}")
    
    
#detect images file exists or not
def detect_file(path):
    import os
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[INFO] {path} created successfully")
    else:
        print(f"[INFO] {path} already exists")
        
def detect_txt_file(path):
    import os
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write('')
        print(f"[INFO] {path} created successfully")
    else:
        print(f"[INFO] {path} already exists")

#Page actions
def  page_actions(url='https://www.bilibili.com/blackboard/activity-award-exchange.html?task_id=7592a5ca'):
    print(f"[INFO] Going to {url}")
    try:
        page.get(url)
        print(f"[INFO] Page loaded successfully")
    except Exception as e:
        raise e
    
    
#Listen for packets
def listen_for_cookies():
    print('[INFO] Listening for packets')
    time.sleep(1)
    page.refresh()
    page.listen.start('csrf')
    for packet in page.listen.steps():
        cookies = packet.request.cookies
        if cookies:
            print('[INFO] Cookies received','\n',cookies)
            cookies_convert(cookies)
            find_str(str(packet))
            if csrf and id:
                print(f"[INFO]csrf and id found, csrf: {csrf}, id: {id}")
                page.listen.stop()
                break
            else:
                print('[WARNING] csrf or id not found')
                time.sleep(1)
                page.refresh()
        else:
            print('[WARNING] Cookies not received')
            time.sleep(1)
            page.refresh()
    return 0



#Find csrf and id
def find_str(packet):
    global csrf,id
    _csrf_str = "csrf="
    _id_str = "id=" 
    _csrf_pos = packet.find(_csrf_str)
    _id_pos = packet.find(_id_str)
    csrf = packet[_csrf_pos+len(_csrf_str):_id_pos].strip('&')
    id = packet[_id_pos+len(_id_str):-2].strip('&')
    
    
    
#Convert dict cookies to str
def cookies_convert(cookies):
    global cookies_str
    cookies_str=""
    for i in cookies:
        cookies_str+=i['name']+'='+i['value']+';'
    print(f"[INFO]Cookies converted: {cookies_str}")

def WaitUntilCanCollectAward() -> bool: 
    from requests import get
    print('[INFO]Start requesting...')
    _url = f"https://api.bilibili.com/x/activity/mission/single_task?csrf={csrf}&id={id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "cookie": cookies_str,
    }
    res = get(_url, headers=headers).json()
    flag = res['data']['task_info']['receive_id']
    while(flag == 0):
        time.sleep(1)
        res = get(_url, headers=headers).json()
        flag = res['data']['task_info']['receive_id']
        print(f"[INFO]{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))} Waiting for award, flag: {flag}")
    print(f"[INFO]{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))} Award is available, flag: {flag}")
    return True
    
def CollectAward():
    _awardSuccessEle= 'x://div[contains(@class, "content-title") and text()="领取成功"]'
    _geetestWidget = 'x://div[contains(@class,"geetest_widge")]'
    while(page.wait.ele_displayed("x://div[contains(@class, 'button exchange-button')]")==False):
        print('[INFO]The Award Collect button is not disabled,retrying...')
        time.sleep(0.1)
        page.refresh()
    print('[INFO]Award button found,clicking...')
    while(page.wait.ele_displayed(_awardSuccessEle,timeout=0.01)==False):
        if(page.wait.ele_displayed(_geetestWidget,timeout=0.1)==True):
            print('[INFO]Geetest widget found...')
            geetest()
        page.ele("x://div[contains(@class, 'button exchange-button')]").click()
    print('[INFO]Award collected successfully')


def geetest():
    geetest_widget_screenshot()
    jpg_crop(img_path=img_path)
    get_geetest_results()
    click_geetest_button()
    if(click_geetest_commit_button()):
        print('[INFO]geetest passed')
    
def geetest_widget_screenshot(max_retry=10):
    global img_path
    img_path = './images/geetest_widge.png'
    _retry = 0
    print("[INFO]Getting a geetest widget screenshot...")
    while(_retry<max_retry):
        try:
            print(f"[INFO]Trying to get a screenshot, retry: {_retry+1}/{max_retry}")
            page.ele('x://div[contains(@class,"geetest_widge")]').get_screenshot(img_path)
            print('[INFO]Screenshot saved to ./images/geetest_widge.png')
            break
        except Exception as e:
            print(f"[ERROR]Failed to get a screenshot, retrying...{e}")
            _retry+=1
            time.sleep(0.1)
    if(_retry==max_retry):
        print('[ERROR]Failed to get a screenshot, max retry reached.')

def jpg_crop(img_path):
    from PIL import Image
    global cropped_img_path
    cropped_img_path = './images/cropped_img.png'
    img = Image.open(img_path)
    width, height = img.size
    height -= 52
    cropped_img = img.crop((0, 0, width, height))
    cropped_img.save(cropped_img_path)
    print(f'[Success]cropped image saved, path: {cropped_img_path}')
    
def tuling_api(img_path,id):
    #imports
    from requests import post
    import json
    import base64
    #read file and encode it to base64
    with open(img_path, 'rb') as f:
        b64_data = base64.b64encode(f.read())
    b64 = b64_data.decode()
    #data
    _data = {"username":API_username,"password":API_password,"ID":id,"b64":b64}
    _data_json = json.dumps(_data)
    _url = 'http://www.fdyscloud.com.cn/tuling/predict'
    #post request
    try:
        result = json.loads(post(_url, data=_data_json).text)
    except TimeoutError as e:
        raise "[Error]Connection Timeout"
    except Exception as e:
        raise e
    #return result
    if result:
        return result
    else:
        raise "[Error]No result found"  

def get_geetest_results(max_retry=10):
    """init"""
    global geetest_results
    id = '08272733'
    geetest_results = {'result': None}
    retry = 0
    Errors = ['请求失败，错误原因：该图未检测到关键要素，未扣积分，请您重新刷图上传。', '请求失败，错误原因：上传图片需同时包含小字/大字部分，请检查！']
    print('[INFO]Uploading to Tuling API...')
    while True:
        if retry >= max_retry:
            print('[ERROR]Max retry reached, failed to get geetest results.')
            break
        print(f'[INFO]Making attemts, retry: {retry+1}/{max_retry}')
        geetest_results = tuling_api(cropped_img_path,id)
        print(f'[INFO]Tuling API result: {geetest_results}')
        try:
            if geetest_results['result'] in Errors:
                retrys += 1
                print('[INFO]Error found, retrying...')
                continue
        except KeyError:
            break
def click_geetest_button():
    for coordnate in geetest_results.values():
        print(f'[INFO]Clicking on {coordnate}')
        offset_x=coordnate['X坐标值']
        print(f'[INFO]offset_x: {offset_x}')
        offset_y=coordnate['Y坐标值']
        print(f'[INFO]offset_y: {offset_y}')
        _img_obj = 'x://div[contains(@class,"geetest_table_box")]'
        page.ele(_img_obj).click.at(offset_x=offset_x,offset_y=offset_y)
        time.sleep(0.1)
        
def click_geetest_commit_button():
    _commit_button = 'x://div[contains(@class,"geetest_commit_tip") and text()="确认"]'
    if(page.wait.ele_displayed(_commit_button,timeout=0.1)==True):
        page.ele(_commit_button).click()
        print('[INFO]Commit button clicked.')
        return True
    else:
        print('[ERROR]Commit button not found.')
        return False

def print_dhm():
    _dhm_ele = 'x://p[contains(@class,"key select-enable")]'
    print("[INFO]兑换码:",page.ele(_dhm_ele).text)
    
if __name__ == '__main__':
    main()