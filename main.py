#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kivy Test App - 最简单的测试版本
验证构建流程是否正常工作
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

Window.clearcolor = (0.1, 0.1, 0.15, 1)

class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 标题
        title = Label(
            text='情绪周期日历',
            font_size='24sp',
            size_hint_y=0.2,
            color=(1, 0.8, 0.2, 1)
        )
        layout.add_widget(title)
        
        # 状态标签
        self.status_label = Label(
            text='点击按钮测试',
            font_size='16sp',
            size_hint_y=0.3,
            color=(0.8, 0.8, 0.8, 1)
        )
        layout.add_widget(self.status_label)
        
        # 测试按钮
        btn = Button(
            text='点击测试',
            size_hint_y=0.2,
            background_color=(0.2, 0.6, 1, 1)
        )
        btn.bind(on_press=self.on_button_click)
        layout.add_widget(btn)
        
        # 退出按钮
        exit_btn = Button(
            text='退出',
            size_hint_y=0.2,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        exit_btn.bind(on_press=self.stop)
        layout.add_widget(exit_btn)
        
        return layout
    
    def on_button_click(self, instance):
        self.status_label.text = '测试成功！构建流程正常。'

if __name__ == '__main__':
    TestApp().run()
