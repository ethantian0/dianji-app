# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
import uiautomator2 as u2
import time
import traceback
from PIL import Image
import threading

# 配置参数 - 极限性能模式
POSITION_1 = (865, 1065)
POSITION_2 = (1456, 846)
FINAL_POS = (2522, 48)

# 预计算目标颜色RGB值（直接硬编码计算结果）
TARGET_RGB1 = (54, 46, 35)  # #362e23
TARGET_RGB2 = (33, 27, 22)  # #211b16
COLOR_TOLERANCE = 20  # 增大容差提高匹配成功率和速度

# 移除所有延迟
SCAN_INTERVAL = 0
CLICK_DELAY = 0

class AutomationApp(BoxLayout):
    def __init__(self, **kwargs):
        super(AutomationApp, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        
        # 状态标签
        self.status_label = Label(text="准备就绪", font_size=20, size_hint=(1, 0.2))
        self.add_widget(self.status_label)
        
        # 控制按钮
        self.start_button = Button(text="开始自动化", font_size=18, size_hint=(1, 0.2))
        self.start_button.bind(on_press=self.start_automation)
        self.add_widget(self.start_button)
        
        self.stop_button = Button(text="停止自动化", font_size=18, size_hint=(1, 0.2))
        self.stop_button.bind(on_press=self.stop_automation)
        self.stop_button.disabled = True
        self.add_widget(self.stop_button)
        
        # 设备连接
        self.device = None
        self.is_running = False
        self.automation_thread = None
        
        # 尝试连接设备
        self.connect_device()
    
    def connect_device(self):
        try:
            self.device = u2.connect()  # 连接到本地设备
            self.status_label.text = "设备连接成功"
        except Exception as e:
            self.status_label.text = f"设备连接失败: {str(e)}"
    
    def start_automation(self, instance):
        if self.device is None:
            self.status_label.text = "请先连接设备"
            return
        
        self.is_running = True
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.status_label.text = "自动化运行中..."
        
        # 在新线程中运行自动化逻辑
        self.automation_thread = threading.Thread(target=self.automation_loop)
        self.automation_thread.daemon = True
        self.automation_thread.start()
    
    def stop_automation(self, instance):
        self.is_running = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.status_label.text = "自动化已停止"
    
    def automation_loop(self):
        try:
            while self.is_running:
                # 步骤1: 检测位置1
                while self.is_running:
                    # 获取截图
                    img = self.device.screenshot(format='pillow')
                    pixel = img.getpixel(POSITION_1)
                    
                    # 内联颜色检测
                    r, g, b = pixel[:3]
                    if (abs(r - 54) <= COLOR_TOLERANCE and 
                        abs(g - 46) <= COLOR_TOLERANCE and 
                        abs(b - 35) <= COLOR_TOLERANCE):
                        # 立即点击
                        self.device.click(POSITION_1[0], POSITION_1[1])
                        break
                
                if not self.is_running:
                    break
                
                # 步骤2: 检测位置2
                while self.is_running:
                    # 获取截图
                    img = self.device.screenshot(format='pillow')
                    pixel = img.getpixel(POSITION_2)
                    
                    # 内联颜色检测
                    r, g, b = pixel[:3]
                    if (abs(r - 33) <= COLOR_TOLERANCE and 
                        abs(g - 27) <= COLOR_TOLERANCE and 
                        abs(b - 22) <= COLOR_TOLERANCE):
                        # 立即点击
                        self.device.click(POSITION_2[0], POSITION_2[1])
                        break
                
                if not self.is_running:
                    break
                
                # 步骤3: 点击最终位置
                self.device.click(FINAL_POS[0], FINAL_POS[1])
                
                # 一轮完成，等待3秒
                time.sleep(3)
                
        except Exception as e:
            self.status_label.text = f"错误: {str(e)}"
            self.is_running = False
            self.start_button.disabled = False
            self.stop_button.disabled = True

class MyApp(App):
    def build(self):
        Window.clearcolor = (0.9, 0.9, 0.9, 1)
        return AutomationApp()

if __name__ == '__main__':
    MyApp().run()