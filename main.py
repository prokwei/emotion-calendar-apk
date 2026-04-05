# -*- coding: utf-8 -*-
"""
情绪周期日历 - Kivy版
可直接在Kivy Launcher中运行
"""
import json
import os
import datetime
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
from kivy.utils import platform

# 设置窗口大小
Window.size = (360, 640)

# 情绪周期颜色
PERIOD_COLORS = {
    '冰点期': (0.5, 0.5, 0.5, 1),
    '复苏期': (1, 0.65, 0, 1),
    '主升期': (0, 0.7, 0, 1),
    '高潮期': (1, 0.4, 0.4, 1),
    '退潮期': (0.86, 0, 0, 1),
    '混沌期': (0.47, 0.47, 0.47, 1)
}

def calculate_emotion(up, dn, br, mc, promote_rate, avg_premium):
    """计算情绪周期"""
    base_effect = (up - dn) / (up + dn) if (up + dn) > 0 else 0
    money_effect = base_effect + avg_premium
    ice_signal = (1 if dn >= 15 else 0) + (1 if mc <= 2 else 0) + (1 if br >= 0.5 else 0)
    
    if ice_signal >= 2 and money_effect < -0.3:
        return '冰点期', '0%'
    elif dn < 5 and mc >= 3 and br < 0.4 and money_effect >= -0.1:
        return '复苏期', '10%'
    elif mc >= 5 and promote_rate >= 0.6 and br < 0.3 and avg_premium >= 0.03 and money_effect >= 0.4:
        return '主升期', '60%'
    elif mc >= 7 and up >= 80 and avg_premium >= 0.05 and promote_rate >= 0.7:
        return '高潮期', '40%'
    elif br >= 0.45 and avg_premium < 0 and dn >= 10:
        return '退潮期', '清仓'
    else:
        return '混沌期', '观望'

class EmotionCalendarApp(App):
    def build(self):
        self.data = self.load_data()
        self.current_year = datetime.datetime.now().year
        self.current_month = datetime.datetime.now().month
        
        root = BoxLayout(orientation='vertical')
        
        # 标题
        title = Label(text='情绪周期日历', font_size=dp(20), bold=True, size_hint_y=None, height=dp(50))
        root.add_widget(title)
        
        # 月份导航
        nav = BoxLayout(size_hint_y=None, height=dp(40))
        nav.add_widget(Button(text='<', on_press=self.prev_month, size_hint_x=None, width=dp(50)))
        self.month_label = Label(text=f'{self.current_year}年{self.current_month}月', font_size=dp(16))
        nav.add_widget(self.month_label)
        nav.add_widget(Button(text='>', on_press=self.next_month, size_hint_x=None, width=dp(50)))
        root.add_widget(nav)
        
        # 日历
        self.calendar_grid = GridLayout(cols=7, spacing=dp(2))
        root.add_widget(self.calendar_grid)
        
        # 详情面板
        self.detail_label = Label(text='选择日期查看详情', size_hint_y=None, height=dp(150))
        root.add_widget(self.detail_label)
        
        # 按钮
        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10), padding=dp(10))
        btn_box.add_widget(Button(text='添加数据', on_press=self.show_input))
        btn_box.add_widget(Button(text='统计', on_press=self.show_stats))
        root.add_widget(btn_box)
        
        self.selected_date = None
        self.update_calendar()
        
        return root
    
    def load_data(self):
        try:
            with open('emotion_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_data(self):
        with open('emotion_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False)
    
    def update_calendar(self):
        self.calendar_grid.clear_widgets()
        
        # 星期标题
        for day in ['日', '一', '二', '三', '四', '五', '六']:
            self.calendar_grid.add_widget(Label(text=day, bold=True))
        
        # 日期
        first_weekday, days_in_month = monthrange(self.current_year, self.current_month)
        
        for _ in range(first_weekday):
            self.calendar_grid.add_widget(Label())
        
        for day in range(1, days_in_month + 1):
            date_str = f'{self.current_year}{self.current_month:02d}{day:02d}'
            emotion = self.data.get(date_str)
            
            btn = Button(text=str(day), size_hint_y=None, height=dp(40))
            
            if emotion:
                period = emotion.get('period', '混沌期')
                btn.background_color = PERIOD_COLORS.get(period, (0.5, 0.5, 0.5, 1))
            
            btn.bind(on_press=lambda x, d=date_str: self.select_date(d))
            self.calendar_grid.add_widget(btn)
        
        self.month_label.text = f'{self.current_year}年{self.current_month}月'
    
    def select_date(self, date_str):
        self.selected_date = date_str
        emotion = self.data.get(date_str)
        
        if emotion:
            text = f"""{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}
{emotion.get('period', '-')}
涨停: {emotion.get('up', '-')} 跌停: {emotion.get('dn', '-')}
炸板率: {emotion.get('br', 0):.1%}
最高连板: {emotion.get('mc', '-')}板
建议仓位: {emotion.get('position', '-')}"""
        else:
            text = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}\n无数据"
        
        self.detail_label.text = text
    
    def prev_month(self, instance):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar()
    
    def next_month(self, instance):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.update_calendar()
    
    def show_input(self, instance):
        if not self.selected_date:
            self.show_popup('提示', '请先选择日期')
            return
        
        layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        inputs = {}
        fields = [
            ('up', '涨停数', '80'),
            ('dn', '跌停数', '3'),
            ('br', '炸板率(%)', '15'),
            ('mc', '最高连板', '7'),
            ('avg_premium', '昨日涨停溢价(%)', '4.5'),
        ]
        
        for key, label, default in fields:
            box = BoxLayout(size_hint_y=None, height=dp(40))
            box.add_widget(Label(text=label, size_hint_x=0.4))
            inp = TextInput(text=default, multiline=False)
            inputs[key] = inp
            box.add_widget(inp)
            layout.add_widget(box)
        
        def save(instance):
            try:
                up = int(inputs['up'].text)
                dn = int(inputs['dn'].text)
                br = float(inputs['br'].text) / 100
                mc = int(inputs['mc'].text)
                avg_premium = float(inputs['avg_premium'].text) / 100
                
                period, position = calculate_emotion(up, dn, br, mc, 0, avg_premium)
                
                self.data[self.selected_date] = {
                    'up': up, 'dn': dn, 'br': br, 'mc': mc,
                    'avg_premium': avg_premium, 'period': period, 'position': position
                }
                self.save_data()
                self.update_calendar()
                self.select_date(self.selected_date)
                popup.dismiss()
            except Exception as e:
                self.show_popup('错误', str(e))
        
        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_box.add_widget(Button(text='保存', on_press=save))
        btn_box.add_widget(Button(text='取消', on_press=lambda x: popup.dismiss()))
        layout.add_widget(btn_box)
        
        popup = Popup(title='添加数据', content=layout, size_hint=(0.9, 0.7))
        popup.open()
    
    def show_stats(self, instance):
        stats = {}
        for data in self.data.values():
            period = data.get('period', '未知')
            stats[period] = stats.get(period, 0) + 1
        
        if not stats:
            self.show_popup('统计', '暂无数据')
            return
        
        text = '情绪周期统计:\n\n'
        total = sum(stats.values())
        for period, count in sorted(stats.items()):
            pct = count / total * 100
            text += f'{period}: {count}天 ({pct:.1f}%)\n'
        
        self.show_popup('统计', text)
    
    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(0.8, 0.5))
        popup.open()

if __name__ == '__main__':
    EmotionCalendarApp().run()
