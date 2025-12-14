import time
import os

def open_bilibili_spaces(start_uid: int, end_uid: int, delay: float = 1.0):
    """
    循环打开B站用户空间链接
    
    Args:
        start_uid (int): 起始UID
        end_uid (int): 结束UID
        delay (float): 每次打开链接之间的延迟（秒）
    """
    for uid in range(start_uid, end_uid + 1):
        url = f"https://space.bilibili.com/{uid}"
        print(f"正在打开: {url}")
        
        # 使用默认浏览器打开链接
        os.system(f"start {url}")
        
        # 如果不是最后一次循环，则等待指定的延迟时间
        if uid < end_uid:
            print(f"等待 {delay} 秒后继续...")
            time.sleep(delay)
    
    print("所有链接已打开完成！")

if __name__ == "__main__":
    # 设置起始和结束UID
    start_uid = 5012075
    end_uid = 99999999  # 可根据需要修改
    delay_seconds = 2  # 每次打开链接之间的延迟时间（秒）
    
    print(f"开始打开UID从 {start_uid} 到 {end_uid} 的B站用户空间...")
    open_bilibili_spaces(start_uid, end_uid, delay_seconds)