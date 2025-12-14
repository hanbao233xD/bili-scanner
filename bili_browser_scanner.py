import time
import re
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json

def setup_driver():
    """设置Chrome浏览器驱动"""
    chrome_options = Options()
    # 无头模式（可选，取消注释下面一行启用）
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # 设置窗口大小
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        # 使用webdriver-manager自动管理ChromeDriver
        service = Service(ChromeDriverManager().install())
        # 创建驱动实例
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # 设置页面加载超时
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        print(f"初始化Chrome驱动失败: {e}")
        print("请确保已安装Chrome浏览器，或尝试手动安装ChromeDriver")
        raise e

def is_valid_username(username):
    """检查用户名是否为纯英文（包含字母和数字）"""
    return bool(re.match(r'^[a-zA-Z0-9]+$', username))

def save_valid_uids(uid_data):
    """保存符合条件的UID和昵称到本地文件"""
    with open("valid_uids.txt", "a", encoding="utf-8") as f:
        for data in uid_data:
            if isinstance(data, dict):
                # 新格式：包含UID和昵称
                f.write(f"{data['uid']}---{data['nickname']}\n")
            else:
                # 旧格式：只有UID
                f.write(f"{data}\n")
    print(f"已保存 {len(uid_data)} 个符合条件的UID")

def extract_user_info(driver):
    """从页面中提取用户信息"""
    try:
        # 等待页面加载完成，最多等待10秒
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 等待更多内容加载
        time.sleep(1)
        
        # 获取页面标题
        title = driver.title
        print(f"页面标题: {title}")  # 调试信息
        
        # 检查是否为有效的用户空间页面
        if "404" in title or ("找不到" in title and "页面" in title):
            # 可能是404页面或其他错误页面
            return None, None
            
        # 初始化用户名和等级
        username = None
        level = -1
        
        # 方法1: 通过class为"nickname"的元素获取用户名
        try:
            nickname_element = driver.find_element(By.CLASS_NAME, "nickname")
            username = nickname_element.text.strip()
            print(f"从nickname元素提取用户名: {username}")  # 调试信息
        except Exception as e:
            print(f"从nickname元素提取用户名失败: {e}")
            pass
            
        # 方法2: 通过class包含"level-icon"的元素获取等级
        try:
            # 查找所有包含level-icon的元素
            level_icon_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'level-icon')]")
            for element in level_icon_elements:
                class_attr = element.get_attribute("class")
                # 从class属性中提取等级信息，如"sic-BDC_svg-user_level_0"
                level_match = re.search(r'level_(\d+)', class_attr)
                if level_match:
                    level = int(level_match.group(1))
                    print(f"从level-icon元素提取等级: {level}")  # 调试信息
                    break
        except Exception as e:
            print(f"从level-icon元素提取等级失败: {e}")
            pass
            
        # 备用方法: 从页面标题中提取用户名
        if not username:
            if "的个人空间" in title:
                # 提取"的个人空间"之前的部分作为用户名
                username = title.split("的个人空间")[0].strip()
            elif "_" in title and "哔哩哔哩" in title:
                # 格式可能是 "用户名_哔哩哔哩"
                username = title.split("_")[0].strip()
                
        # 备用方法: 从页面源码中提取信息
        if not username or level == -1:
            try:
                page_source = driver.page_source
                # 尝试从页面源码中提取用户名
                if not username:
                    # 查找用户名的几种可能格式
                    username_patterns = [
                        r'"uname":"([^"]+)"',
                        r'"name":"([^"]+)"',
                        r'"username":"([^"]+)"'
                    ]
                    
                    for pattern in username_patterns:
                        username_match = re.search(pattern, page_source)
                        if username_match:
                            username = username_match.group(1)
                            print(f"从源码提取用户名: {username}")  # 调试信息
                            break
                
                # 尝试从页面源码中提取等级
                if level == -1:
                    level_match = re.search(r'"level":(\d+)', page_source)
                    if level_match:
                        level = int(level_match.group(1))
                        print(f"从源码提取等级: {level}")  # 调试信息
            except Exception as e:
                print(f"从源码提取信息失败: {e}")
                pass
        
        # 如果仍然无法获取用户名，尝试从URL获取
        if not username:
            current_url = driver.current_url
            # 从URL中提取UID
            uid_match = re.search(r'space\.bilibili\.com/(\d+)', current_url)
            if uid_match:
                username = f"user_{uid_match.group(1)}"
        
        # 清理用户名，只保留基本字符
        if username:
            # 移除可能的多余后缀
            username = re.sub(r'-.*$', '', username).strip()
            # 如果用户名太长或者看起来不对，设为None
            if len(username) > 50 or len(username) == 0:
                username = None
        
        print(f"最终提取结果 - 用户名: {username}, 等级: {level}")  # 调试信息
        return username, level
    except Exception as e:
        print(f"提取用户信息失败: {e}")
        return None, None

def scan_accounts():
    """扫描符合条件的账号"""
    # 设置驱动
    driver = setup_driver()
    
    # 从UID 1开始扫描
    uid = 5490000
    valid_uids = []
    save_count = 0
    
    # 记录扫描进度
    last_save_uid = 0
    
    try:
        while True:
            print(f"正在扫描 UID: {uid}")
            
            retry_count = 0
            max_retries = 3
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    # 访问用户空间页面
                    url = f"https://space.bilibili.com/{uid}"
                    driver.get(url)
                    
                    # 等待页面加载
                    
                    # 检查是否被拦截（如出现验证码页面）
                    page_source = driver.page_source
                    if "验证码" in page_source or "verify" in page_source.lower():
                        print(f"UID {uid}: 检测到验证码拦截，跳过此UID")
                        success = True
                        break
                    
                    # 提取用户信息
                    username, level = extract_user_info(driver)
                    
                    # 检查是否为有效用户页面
                    if username is not None and level != -1:
                        # 检查条件：等级为0，用户名纯英文
                        if level == 0 and is_valid_username(username):
                            print(f"发现符合条件的账号: UID={uid}, 昵称={username}, 等级={level}")
                            # 保存UID和昵称
                            valid_uids.append({"uid": uid, "nickname": username})
                            save_count += 1
                            
                            # 每1个保存一次
                            if save_count % 1 == 0:
                                save_valid_uids(valid_uids)
                                valid_uids.clear()
                                print(f"已保存 {save_count} 个符合条件的UID")
                                last_save_uid = uid
                        else:
                            print(f"UID {uid}: 昵称={username}, 等级={level} (不符合条件)")
                        success = True
                    else:
                        # 如果没有找到用户信息，可能是用户不存在或页面异常
                        print(f"UID {uid} 可能不存在或页面异常")
                        success = True
                        
                except Exception as e:
                    retry_count += 1
                    print(f"处理 UID {uid} 时出错 (尝试 {retry_count}/{max_retries}): {e}")
                    if retry_count < max_retries:
                        # 随机延迟后重试
                        delay = random.uniform(1, 4)
                        print(f"等待 {delay:.1f} 秒后重试...")
                        time.sleep(delay)
                    else:
                        print(f"UID {uid} 处理失败，已达到最大重试次数")
            
            # 每扫描1000个UID记录一次进度
            if uid % 1000 == 0:
                print(f"扫描进度: 已扫描至 UID {uid}，最后保存UID为 {last_save_uid}")
            
            # 增加UID
            uid += 1
            
            # 避免请求过于频繁，设置随机延迟
            delay = random.uniform(1, 2)
            time.sleep(delay)
            
    except KeyboardInterrupt:
        print("\n扫描已停止")
        # 保存剩余的UID
        if valid_uids:
            save_valid_uids(valid_uids)
            print(f"已保存最后 {len(valid_uids)} 个符合条件的UID")
    finally:
        # 关闭浏览器
        driver.quit()

if __name__ == "__main__":
    scan_accounts()