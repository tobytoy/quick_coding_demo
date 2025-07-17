import streamlit as st
import re
from typing import List, Dict, Optional
import json

class DartWidgetAnalyzer:
    def __init__(self):
        # 常見的 Flutter widgets
        self.common_widgets = {
            'MaterialApp', 'Scaffold', 'AppBar', 'Body', 'Column', 'Row', 'Container',
            'Text', 'Button', 'ElevatedButton', 'TextButton', 'OutlinedButton',
            'TextField', 'Image', 'Icon', 'ListView', 'GridView', 'Stack',
            'Positioned', 'Padding', 'Margin', 'Center', 'Align', 'Expanded',
            'Flexible', 'SizedBox', 'Card', 'ListTile', 'Drawer', 'FloatingActionButton',
            'BottomNavigationBar', 'TabBar', 'TabBarView', 'SingleChildScrollView',
            'CustomScrollView', 'Sliver', 'SliverAppBar', 'SliverList', 'SliverGrid',
            'GestureDetector', 'InkWell', 'Hero', 'AnimatedContainer', 'FadeTransition',
            'SlideTransition', 'ScaleTransition', 'RotationTransition', 'AnimatedBuilder',
            'StreamBuilder', 'FutureBuilder', 'StatefulWidget', 'StatelessWidget',
            'Widget', 'BuildContext', 'SafeArea', 'ClipRRect', 'DecoratedBox',
            'Transform', 'Opacity', 'Visibility', 'Wrap', 'Chip', 'ChoiceChip',
            'FilterChip', 'ActionChip', 'InputChip', 'CircularProgressIndicator',
            'LinearProgressIndicator', 'RefreshIndicator', 'Dismissible', 'Stepper',
            'Step', 'ExpansionTile', 'ExpansionPanel', 'DataTable', 'DataRow',
            'DataCell', 'CheckboxListTile', 'RadioListTile', 'SwitchListTile',
            'Slider', 'RangeSlider', 'DatePicker', 'TimePicker', 'ShowDialog',
            'AlertDialog', 'SimpleDialog', 'BottomSheet', 'ModalBottomSheet',
            'Snackbar', 'Tooltip', 'PopupMenuButton', 'DropdownButton', 'Autocomplete'
        }
    
    def extract_widgets(self, code: str) -> List[Dict]:
        """從 Dart 程式碼中提取 widget 結構"""
        # 移除註解
        code = re.sub(r'//.*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # 找出所有可能的 widget 實例化
        widgets = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 尋找 widget 實例化模式
            for widget_name in self.common_widgets:
                patterns = [
                    rf'{widget_name}\s*\(',  # WidgetName(
                    rf'new\s+{widget_name}\s*\(',  # new WidgetName(
                    rf'return\s+{widget_name}\s*\(',  # return WidgetName(
                    rf'=\s*{widget_name}\s*\(',  # = WidgetName(
                ]
                
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # 計算縮排級別來判斷層級
                        indent_level = len(line) - len(line.lstrip())
                        widgets.append({
                            'name': widget_name,
                            'line': i + 1,
                            'indent': indent_level,
                            'code': line.strip()
                        })
                        break
        
        return widgets
    
    def build_tree_structure(self, widgets: List[Dict]) -> Dict:
        """將扁平的 widget 列表轉換為樹狀結構"""
        if not widgets:
            return {}
        
        root = {'name': 'Root', 'children': []}
        stack = [root]
        
        for widget in widgets:
            current_level = widget['indent']
            
            # 調整 stack 到適當的父節點
            while len(stack) > 1 and stack[-1].get('indent', 0) >= current_level:
                stack.pop()
            
            # 創建新節點
            node = {
                'name': widget['name'],
                'line': widget['line'],
                'indent': current_level,
                'code': widget['code'],
                'children': []
            }
            
            # 添加到父節點
            stack[-1]['children'].append(node)
            stack.append(node)
        
        return root
    
    def render_tree_html(self, node: Dict, level: int = 0) -> str:
        """將樹狀結構轉換為 HTML"""
        if not node:
            return ""
        
        indent = "  " * level
        html = ""
        
        if node['name'] != 'Root':
            color = self.get_widget_color(node['name'])
            html += f"{indent}<div style='margin-left: {level * 20}px; margin-bottom: 5px;'>\n"
            html += f"{indent}  <span style='color: {color}; font-weight: bold;'>{node['name']}</span>\n"
            html += f"{indent}  <span style='color: #666; font-size: 0.9em;'> (Line {node['line']})</span>\n"
            html += f"{indent}  <div style='color: #888; font-size: 0.8em; margin-top: 2px;'>{node['code']}</div>\n"
            html += f"{indent}</div>\n"
        
        for child in node.get('children', []):
            html += self.render_tree_html(child, level + 1)
        
        return html
    
    def get_widget_color(self, widget_name: str) -> str:
        """為不同類型的 widget 分配顏色"""
        layout_widgets = {'Column', 'Row', 'Stack', 'Container', 'Padding', 'Center', 'Align', 'Expanded', 'Flexible'}
        ui_widgets = {'Text', 'Button', 'ElevatedButton', 'TextButton', 'OutlinedButton', 'TextField', 'Image', 'Icon'}
        structure_widgets = {'MaterialApp', 'Scaffold', 'AppBar', 'Drawer', 'FloatingActionButton'}
        
        if widget_name in structure_widgets:
            return '#2196F3'  # 藍色
        elif widget_name in layout_widgets:
            return '#4CAF50'  # 綠色
        elif widget_name in ui_widgets:
            return '#FF9800'  # 橙色
        else:
            return '#9C27B0'  # 紫色

def main():
    st.set_page_config(
        page_title="Dart Widget Tree Analyzer",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Dart Widget Tree Analyzer")
    st.markdown("貼上你的 Dart Flutter 程式碼，在右邊查看 Widget Tree 結構")
    
    # 創建兩列佈局
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Dart 程式碼")
        
        # 提供範例程式碼
        sample_code = """
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Flutter Demo Home Page'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              'You have pushed the button this many times:',
            ),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headline4,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: Icon(Icons.add),
      ),
    );
  }
}
"""
        
        # 程式碼輸入區域
        code_input = st.text_area(
            "貼上你的 Dart 程式碼：",
            value=sample_code,
            height=400,
            help="貼上包含 Flutter widgets 的 Dart 程式碼"
        )
        
        # 分析選項
        st.subheader("⚙️ 分析選項")
        show_line_numbers = st.checkbox("顯示行號", value=True)
        show_code_preview = st.checkbox("顯示程式碼預覽", value=True)
        
        # 分析按鈕
        analyze_button = st.button("🔍 分析 Widget Tree", type="primary")
    
    with col2:
        st.subheader("🌳 Widget Tree")
        
        if analyze_button or code_input:
            analyzer = DartWidgetAnalyzer()
            
            # 提取 widgets
            widgets = analyzer.extract_widgets(code_input)
            
            if widgets:
                # 建構樹狀結構
                tree_structure = analyzer.build_tree_structure(widgets)
                
                # 顯示統計資訊
                st.info(f"找到 {len(widgets)} 個 widgets")
                
                # 渲染樹狀結構
                tree_html = analyzer.render_tree_html(tree_structure)
                
                # 顯示樹狀結構
                st.markdown(
                    f"""
                    <div style='
                        background-color: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 5px;
                        padding: 15px;
                        font-family: monospace;
                        max-height: 500px;
                        overflow-y: auto;
                    '>
                        {tree_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # 顯示 widget 統計
                st.subheader("📊 Widget 統計")
                widget_counts = {}
                for widget in widgets:
                    widget_counts[widget['name']] = widget_counts.get(widget['name'], 0) + 1
                
                for widget_name, count in sorted(widget_counts.items()):
                    st.write(f"• {widget_name}: {count}")
                
            else:
                st.warning("未找到任何 Flutter widgets，請檢查你的程式碼。")
                st.info("確保你的程式碼包含常見的 Flutter widgets，如 MaterialApp, Scaffold, Text, Column, Row 等。")
    
    # 側邊欄說明
    with st.sidebar:
        st.header("📚 使用說明")
        st.markdown("""
        1. **貼上程式碼**: 在左側文字區域貼上你的 Dart Flutter 程式碼
        2. **分析結果**: 右側會顯示 Widget Tree 結構
        3. **顏色說明**:
           - 🔵 藍色: 結構型 widgets (MaterialApp, Scaffold 等)
           - 🟢 綠色: 佈局型 widgets (Column, Row, Container 等)
           - 🟠 橙色: UI 元件 widgets (Text, Button 等)
           - 🟣 紫色: 其他 widgets
        """)
        
        st.header("🎯 支援的 Widgets")
        st.markdown("工具支援大部分常見的 Flutter widgets，包括:")
        st.markdown("• 佈局: Column, Row, Stack, Container")
        st.markdown("• UI 元件: Text, Button, TextField, Image")
        st.markdown("• 結構: MaterialApp, Scaffold, AppBar")
        st.markdown("• 導航: Drawer, BottomNavigationBar")
        st.markdown("• 以及更多...")

if __name__ == "__main__":
    main()