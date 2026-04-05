# -*- coding: utf-8 -*-
"""
情绪周期日历 - Kivy简化版
移除akshare/pandas/numpy依赖，纯Kivy实现
"""
import json
import os
from datetime import datetime, timedelta
from calendar import monthrange

# Kivy导入
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock

# 设置窗口大小（手机竖屏比例）
Window.size = (360, 640)

# ==================== 数据管理 ====================
class DataManager:
    """管理情绪周期数据（JSON文件存储）"""
    
    DATA_FILE = "emotion_data.json"
    
    def __init__(self):
        self.data = self.load()
    
    def load(self):
        """加载数据"""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save(self):
        """保存数据"""
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get(self, date_str):
        """获取某日数据"""
        return self.data.get(date_str)
    
    def set(self, date_str, emotion_data):
        """设置某日数据"""
        self.data[date_str] = emotion_data
        self.save()
    
    def get_all(self):
        """获取所有数据"""
        return self.data

# ==================== 情绪周期判定 ====================
def judge_period(data):
    """判定情绪周期"""
    up = data.get('up', 0)
    dn = data.get('dn', 0)
    zb = data.get('zb', 0)
    mc = data.get('mc', 0)
    promote_rate = data.get('promote_rate', 0)
    avg_premium = data.get('avg_premium', 0)
    
    # 计算炸板率
    br = zb / (up + zb + 1) if (up + zb) > 0 else 0
    
    # 赚钱效应
    money_effect = (up - dn) / (up + dn + 1) if (up + dn) > 0 else 0
    
    # 冰点期：跌停>=10 且 赚钱效应<-0.3
    if dn >= 10 and money_effect < -0.3:
        return {'period': '冰点期', 'color': '#808080', 'position': '0%'}
    
    # 复苏期：跌停<5 且 连板>=3 且 炸板<40% 且 赚钱效应>=-0.1
    if dn < 5 and mc >= 3 and br < 0.4 and money_effect >= -0.1:
        return {'period': '复苏期', 'color': '#FFA500', 'position': '10%'}
    
    # 主升期：连板>=5 且 晋级>=60% 且 炸板<30% 且 溢价>=3% 且 赚钱效应>=0.4
    if mc >= 5 and promote_rate >= 0.6 and br < 0.3 and avg_premium >= 0.03 and money_effect >= 0.4:
        return {'period': '主升期', 'color': '#00B400', 'position': '60%'}
    
    # 高潮期：连板>=7 且 涨停>=80 且 溢价>=5% 且 晋级>=70%
    if mc >= 7 and up >= 80 and avg_premium >= 0.05 and promote_rate >= 0.7:
        return {'period': '高潮期', 'color': '#FF6464', 'position': '40%'}
    
    # 退潮期：炸板>=45% 且 溢价<0 且 跌停>=10
    if br >= 0.45 and avg_premium < 0 and dn >= 10:
        return {'period': '退潮期', 'color': '#DC0000', 'position': '0%'}
    
    # 混沌期
    return {'period': '混沌期', 'color': '#787878', 'position': '0%'}

# ==================== UI组件 ====================
class DayButton(Button):
    """日历日期按钮"""
    date_str = StringProperty('')
    period_color = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (1, 1, 1, 1)
        self.color = (0.2, 0.2, 0.2, 1)
        self.font_size = dp(14)

class EmotionCalendarApp(App):
    """情绪周期日历应用"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = DataManager()
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.selected_date = None
    
    def build(self):
        """构建UI"""
        self.title = '情绪周期日历'
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # 标题
        title = Label(
            text='情绪周期日历',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.2, 0.2, 1)
        )
        main_layout.add_widget(title)
        
        # 月份导航
        nav_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        
        self.prev_btn = Button(text='<', size_hint_x=None, width=dp(40))
        self.prev_btn.bind(on_press=self.prev_month)
        
        self.month_label = Label(
            text=f'{self.current_year}年{self.current_month}月',
            font_size=dp(16),
            color=(0.2, 0.2, 0.2, 1)
        )
        
        self.next_btn = Button(text='>', size_hint_x=None, width=dp(40))
        self.next_btn.bind(on_press=self.next_month)
        
        today_btn = Button(text='今天', size_hint_x=None, width=dp(60))
        today_btn.bind(on_press=self.go_today)
        
        nav_layout.add_widget(self.prev_btn)
        nav_layout.add_widget(self.month_label)
        nav_layout.add_widget(self.next_btn)
        nav_layout.add_widget(today_btn)
        main_layout.add_widget(nav_layout)
        
        # 星期标题
        week_layout = GridLayout(cols=7, size_hint_y=None, height=dp(30))
        weekdays = ['日', '一', '二', '三', '四', '五', '六']
        for day in weekdays:
            label = Label(
                text=day,
                font_size=dp(12),
                color=(0.4, 0.4, 0.4, 1)
            )
            week_layout.add_widget(label)
        main_layout.add_widget(week_layout)
        
        # 日历网格
        self.calendar_grid = GridLayout(cols=7, spacing=dp(2))
        main_layout.add_widget(self.calendar_grid)
        
        # 选中日期信息
        self.info_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150),
            padding=dp(10),
            spacing=dp(5)
        )
        
        with self.info_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.info_rect = Rectangle(size=self.info_layout.size, pos=self.info_layout.pos)
        self.info_layout.bind(size=self._update_info_rect, pos=self._update_info_rect)
        
        self.date_label = Label(
            text='请选择日期',
            font_size=dp(14),
            size_hint_y=None,
            height=dp(25),
            color=(0.2, 0.2, 0.2, 1)
        )
        self.info_layout.add_widget(self.date_label)
        
        self.period_label = Label(
            text='',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(30),
            bold=True
        )
        self.info_layout.add_widget(self.period_label)
        
        self.position_label = Label(
            text='',
            font_size=dp(12),
            size_hint_y=None,
            height=dp(20),
            color=(0.5, 0.5, 0.5, 1)
        )
        self.info_layout.add_widget(self.position_label)
        
        edit_btn = Button(
            text='编辑数据',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.17, 0.24, 0.31, 1)
        )
        edit_btn.bind(on_press=self.show_edit_popup)
        self.info_layout.add_widget(edit_btn)
        
        main_layout.add_widget(self.info_layout)
        
        # 图例
        legend_layout = GridLayout(cols=3, size_hint_y=None, height=dp(80), spacing=dp(5))
        periods = [
            ('冰点期', '#808080'),
            ('复苏期', '#FFA500'),
            ('主升期', '#00B400'),
            ('高潮期', '#FF6464'),
            ('退潮期', '#DC0000'),
            ('混沌期', '#787878')
        ]
        for name, color in periods:
            box = BoxLayout(padding=dp(5))
            with box.canvas.before:
                Color(*self.hex_to_rgb(color))
                rect = Rectangle(size=box.size, pos=box.pos)
            box.bind(size=lambda obj, val, r=rect: self._update_rect_color(obj, r), 
                     pos=lambda obj, val, r=rect: self._update_rect_color(obj, r))
            label = Label(text=name, font_size=dp(10), color=(1, 1, 1, 1))
            box.add_widget(label)
            legend_layout.add_widget(box)
        main_layout.add_widget(legend_layout)
        
        # 生成日历
        self.generate_calendar()
        
        # 选中今天
        today = datetime.now()
        self.select_date(today.strftime('%Y%m%d'))
        
        return main_layout
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def _update_info_rect(self, instance, value):
        self.info_rect.pos = instance.pos
        self.info_rect.size = instance.size
    
    def _update_rect_color(self, instance, rect):
        rect.pos = instance.pos
        rect.size = instance.size
    
    def hex_to_rgb(self, hex_color):
        """十六进制颜色转RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4)) + (1,)
    
    def generate_calendar(self):
        """生成日历"""
        self.calendar_grid.clear_widgets()
        
        # 获取月份第一天和天数
        first_day = datetime(self.current_year, self.current_month, 1)
        days_in_month = monthrange(self.current_year, self.current_month)[1]
        start_weekday = first_day.weekday()
        
        # 调整星期（周一=0 改为 周日=0）
        start_weekday = (start_weekday + 1) % 7
        
        # 上月填充
        if start_weekday > 0:
            prev_month = self.current_month - 1
            prev_year = self.current_year
            if prev_month < 1:
                prev_month = 12
                prev_year -= 1
            prev_days = monthrange(prev_year, prev_month)[1]
            for i in range(start_weekday):
                btn = DayButton(text=str(prev_days - start_weekday + i + 1))
                btn.disabled = True
                btn.background_color = (0.9, 0.9, 0.9, 1)
                self.calendar_grid.add_widget(btn)
        
        # 当月
        today = datetime.now()
        for day in range(1, days_in_month + 1):
            date_str = f'{self.current_year}{self.current_month:02d}{day:02d}'
            btn = DayButton(text=str(day), date_str=date_str)
            
            # 检查是否有数据
            data = self.data_manager.get(date_str)
            if data:
                result = judge_period(data)
                btn.period_color = result['color']
                btn.background_color = self.hex_to_rgb(result['color'])
                btn.color = (1, 1, 1, 1)
            
            # 标记今天
            if today.year == self.current_year and today.month == self.current_month and today.day == day:
                btn.bold = True
            
            btn.bind(on_press=self.on_day_click)
            self.calendar_grid.add_widget(btn)
        
        # 下月填充
        remaining = 42 - start_weekday - days_in_month
        for i in range(remaining):
            btn = DayButton(text=str(i + 1))
            btn.disabled = True
            btn.background_color = (0.9, 0.9, 0.9, 1)
            self.calendar_grid.add_widget(btn)
    
    def on_day_click(self, instance):
        """日期点击"""
        if not instance.disabled:
            self.select_date(instance.date_str)
    
    def select_date(self, date_str):
        """选中日期"""
        self.selected_date = date_str
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        
        self.date_label.text = f'{year}年{int(month)}月{int(day)}日'
        
        data = self.data_manager.get(date_str)
        if data:
            result = judge_period(data)
            self.period_label.text = result['period']
            self.period_label.color = self.hex_to_rgb(result['color'])
            self.position_label.text = f'建议仓位: {result["position"]}'
        else:
            self.period_label.text = '暂无数据'
            self.period_label.color = (0.5, 0.5, 0.5, 1)
            self.position_label.text = '点击编辑添加数据'
    
    def prev_month(self, instance):
        """上月"""
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_month()
    
    def next_month(self, instance):
        """下月"""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.update_month()
    
    def go_today(self, instance):
        """今天"""
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        self.update_month()
        self.select_date(today.strftime('%Y%m%d'))
    
    def update_month(self):
        """更新月份显示"""
        self.month_label.text = f'{self.current_year}年{self.current_month}月'
        self.generate_calendar()
    
    def show_edit_popup(self, instance):
        """显示编辑弹窗"""
        if not self.selected_date:
            return
        
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 加载已有数据
        existing = self.data_manager.get(self.selected_date) or {}
        
        # 表单字段
        fields = {}
        field_names = [
            ('up', '涨停数'),
            ('dn', '跌停数'),
            ('zb', '炸板数'),
            ('mc', '连板高度'),
            ('promote_rate', '晋级率(0-1)'),
            ('avg_premium', '昨日涨停溢价(如0.03)')
        ]
        
        for key, label in field_names:
            layout = BoxLayout(size_hint_y=None, height=dp(40))
            lbl = Label(text=label, size_hint_x=None, width=dp(120), color=(0.2, 0.2, 0.2, 1))
            txt = TextInput(
                text=str(existing.get(key, '')),
                multiline=False,
                input_filter='float' if key in ['promote_rate', 'avg_premium'] else 'int'
            )
            layout.add_widget(lbl)
            layout.add_widget(txt)
            content.add_widget(layout)
            fields[key] = txt
        
        # 按钮
        btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        
        save_btn = Button(text='保存', background_color=(0.17, 0.24, 0.31, 1))
        cancel_btn = Button(text='取消', background_color=(0.7, 0.7, 0.7, 1))
        
        popup = Popup(title='编辑情绪数据', content=content, size_hint=(0.9, 0.8))
        
        def save(instance):
            data = {}
            for key, txt in fields.items():
                try:
                    if key in ['promote_rate', 'avg_premium']:
                        data[key] = float(txt.text) if txt.text else 0
                    else:
                        data[key] = int(txt.text) if txt.text else 0
                except:
                    data[key] = 0
            
            self.data_manager.set(self.selected_date, data)
            self.select_date(self.selected_date)
            self.generate_calendar()
            popup.dismiss()
        
        save_btn.bind(on_press=save)
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup.open()

# ==================== 启动应用 ====================
if __name__ == '__main__':
    EmotionCalendarApp().run()
