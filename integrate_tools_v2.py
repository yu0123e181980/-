#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8つのHTMLツールを1つに統合するスクリプト (改良版)
各ツールの完全な機能を維持しながら、タブで切り替えられる統合ツールを作成
"""

import re
from pathlib import Path
from html.parser import HTMLParser

# 統合するファイルのリスト
tools = [
    {'file': '⓪棚割データ処理ツール.html', 'name': '棚割データ処理', 'id': 'tool0'},
    {'file': '①非定型月次データ可視化ツール.html', 'name': '月次データ可視化', 'id': 'tool1'},
    {'file': '②売上分解ツール 表形式ver.html', 'name': '売上分解(表)', 'id': 'tool2'},
    {'file': '②売上分解ツール 分解ツリーver.html', 'name': '売上分解(ツリー)', 'id': 'tool3'},
    {'file': '③顧客属性詳細分析ツール.html', 'name': '顧客属性分析', 'id': 'tool4'},
    {'file': '④Visual_Benchmarking_tool.html', 'name': 'Benchmarking', 'id': 'tool5'},
    {'file': '⑤エリア特化商品選定ツール.html', 'name': 'エリア特化商品', 'id': 'tool6'},
    {'file': '⑥ABC分析ツール.html', 'name': 'ABC分析', 'id': 'tool7'}
]

def read_html_file(filepath):
    """HTMLファイルを読み込んで、style、body、scriptを抽出"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # styleタグ抽出
    styles = []
    for match in re.finditer(r'<style[^>]*>(.*?)</style>', content, re.DOTALL | re.IGNORECASE):
        styles.append(match.group(1))

    # bodyタグの内容を抽出
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    body = body_match.group(1) if body_match else ''

    # scriptタグ抽出（srcのないもののみ）
    scripts = []
    for match in re.finditer(r'<script(?![^>]*\ssrc=)[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE):
        scripts.append(match.group(1))

    return {
        'styles': '\n'.join(styles),
        'body': body,
        'scripts': '\n\n'.join(scripts)
    }

def clean_body_content(body_html):
    """bodyからスプラッシュスクリーンとモーダルを除去"""
    # スプラッシュスクリーン除去
    body_html = re.sub(
        r'<div[^>]*id=["\']splashScreen["\'][^>]*>.*?</div>\s*',
        '',
        body_html,
        flags=re.DOTALL | re.IGNORECASE
    )

    # 外部ライブラリ確認モーダル除去
    body_html = re.sub(
        r'<div[^>]*id=["\']confirmModal["\'][^>]*>.*?</div>\s*',
        '',
        body_html,
        flags=re.DOTALL | re.IGNORECASE
    )

    # loading message除去
    body_html = re.sub(
        r'<div[^>]*id=["\']loadingMessage["\'][^>]*>.*?</div>\s*',
        '',
        body_html,
        flags=re.DOTALL | re.IGNORECASE
    )

    # error message除去
    body_html = re.sub(
        r'<div[^>]*id=["\']errorMessage["\'][^>]*>.*?</div>\s*',
        '',
        body_html,
        flags=re.DOTALL | re.IGNORECASE
    )

    return body_html

def scope_css(css_text, tool_id):
    """CSSをツール専用にスコープ化"""
    # グローバルセレクタ(*, body, htmlなど)はそのまま保持
    # その他のセレクタには #tool_id をプレフィックスとして追加

    lines = []
    current_line = ""

    for line in css_text.split('\n'):
        stripped = line.strip()

        # コメントやアットルールはそのまま
        if stripped.startswith('/*') or stripped.startswith('*/') or stripped.startswith('@'):
            lines.append(line)
            continue

        # セレクタ行の検出（{を含む行）
        if '{' in line and not line.strip().startswith('/*'):
            # セレクタ部分を取得
            selector_part = line.split('{')[0]
            rest_part = '{' + '{'.join(line.split('{')[1:])

            # グローバルセレクタはスコープ化しない
            if any(selector_part.strip().startswith(x) for x in ['*', 'html', 'body', ':root']):
                lines.append(line)
            else:
                # セレクタにスコープを追加
                selectors = [s.strip() for s in selector_part.split(',')]
                scoped_selectors = []
                for sel in selectors:
                    if sel:
                        # keyframesなどは除外
                        if not any(x in sel for x in ['@keyframes', '@media', '@font-face']):
                            scoped_selectors.append(f'#{tool_id} {sel}')
                        else:
                            scoped_selectors.append(sel)

                if scoped_selectors:
                    lines.append(', '.join(scoped_selectors) + rest_part)
                else:
                    lines.append(line)
        else:
            lines.append(line)

    return '\n'.join(lines)

def create_integrated_html():
    """統合HTMLファイルを作成"""

    # 各ツールの読み込み
    print("ツールを読み込んでいます...")
    tool_data = []
    for tool_info in tools:
        filepath = Path(tool_info['file'])
        if filepath.exists():
            print(f"  {tool_info['name']}...")
            data = read_html_file(filepath)
            tool_data.append({
                **tool_info,
                **data
            })
        else:
            print(f"  警告: {tool_info['file']} が見つかりません")

    # HTMLの構築開始
    html_parts = []

    # DOCTYPE and HTML header
    html_parts.append('''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>統合分析ツール</title>
    <style>
        /* ========== 共通スタイル ========== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: "Hiragino Sans", "Yu Gothic", "Meiryo", "MS PGothic", sans-serif;
            background: #f5f5f5;
        }

        .hidden {
            display: none !important;
        }

        /* ========== スプラッシュスクリーン ========== */
        .splash-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #1F5F8B 0%, #2C7FB8 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 30000;
            animation: fadeOut 0.5s ease-out 2s forwards;
        }

        @keyframes fadeOut {
            to {
                opacity: 0;
                visibility: hidden;
            }
        }

        .splash-content {
            text-align: center;
        }

        .splash-title {
            color: white;
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 40px;
            opacity: 0;
            animation: fadeInUp 0.6s ease-out 0.2s forwards;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .chart-animation {
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 8px;
            height: 120px;
            margin-bottom: 30px;
        }

        .bar {
            width: 20px;
            background: white;
            border-radius: 3px 3px 0 0;
            opacity: 0.9;
            animation: growBar 0.8s ease-out forwards;
        }

        .bar:nth-child(1) { height: 60px; animation-delay: 0.3s; }
        .bar:nth-child(2) { height: 90px; animation-delay: 0.4s; }
        .bar:nth-child(3) { height: 45px; animation-delay: 0.5s; }
        .bar:nth-child(4) { height: 75px; animation-delay: 0.6s; }
        .bar:nth-child(5) { height: 100px; animation-delay: 0.7s; }
        .bar:nth-child(6) { height: 55px; animation-delay: 0.8s; }

        @keyframes growBar {
            from {
                transform: scaleY(0);
                opacity: 0;
            }
            to {
                transform: scaleY(1);
                opacity: 0.9;
            }
        }

        .loading-text {
            color: white;
            font-size: 14px;
            opacity: 0;
            animation: fadeIn 0.5s ease-out 1.5s forwards;
        }

        @keyframes fadeIn {
            to {
                opacity: 0.8;
            }
        }

        /* ========== モーダル ========== */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 20000;
        }

        .modal {
            background: white;
            padding: 30px;
            border-radius: 8px;
            max-width: 700px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .modal h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 20px;
        }

        .modal-content {
            margin-bottom: 25px;
            line-height: 1.8;
            color: #555;
        }

        .library-list {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
            border-left: 4px solid #1F5F8B;
        }

        .library-list li {
            margin: 8px 0;
            color: #333;
        }

        .security-info {
            background: #e8f5e9;
            padding: 12px;
            border-radius: 4px;
            margin: 15px 0;
            border-left: 4px solid #4CAF50;
            font-size: 14px;
        }

        .modal-buttons {
            display: flex;
            gap: 15px;
            justify-content: flex-end;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: all 0.3s;
        }

        .btn-primary {
            background: #1F5F8B;
            color: white;
        }

        .btn-primary:hover {
            background: #164563;
        }

        .btn-secondary {
            background: #ddd;
            color: #333;
        }

        .btn-secondary:hover {
            background: #ccc;
        }

        .loading-message {
            text-align: center;
            padding: 40px;
            color: #666;
        }

        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #1F5F8B;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error-message {
            background: #ffebee;
            padding: 20px;
            border-radius: 4px;
            border-left: 4px solid #f44336;
            color: #c62828;
        }

        /* ========== タブナビゲーション ========== */
        .tab-navigation {
            background: white;
            border-bottom: 2px solid #1F5F8B;
            display: flex;
            overflow-x: auto;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .tab {
            padding: 15px 25px;
            cursor: pointer;
            border: none;
            background: #f5f5f5;
            color: #555;
            font-weight: bold;
            font-size: 14px;
            white-space: nowrap;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }

        .tab:hover {
            background: #e8e8e8;
        }

        .tab.active {
            background: white;
            color: #1F5F8B;
            border-bottom-color: #1F5F8B;
        }

        /* ========== ツールコンテンツ ========== */
        .tool-content {
            display: none;
        }

        .tool-content.active {
            display: block;
            animation: fadeInContent 0.3s ease-in;
        }

        @keyframes fadeInContent {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
''')

    # 各ツールのスタイルを追加
    print("\nスタイルを統合しています...")
    for tool in tool_data:
        print(f"  {tool['name']}のスタイル...")
        html_parts.append(f"\n        /* ========== {tool['name']} スタイル ========== */")
        scoped_styles = scope_css(tool['styles'], tool['id'])
        html_parts.append(scoped_styles)

    html_parts.append('''
    </style>
</head>
<body>
    <!-- スプラッシュスクリーン -->
    <div id="splashScreen" class="splash-screen">
        <div class="splash-content">
            <div class="splash-title">統合分析ツール</div>
            <div class="chart-animation">
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
                <div class="bar"></div>
            </div>
            <div class="loading-text">Loading...</div>
        </div>
    </div>

    <!-- ライブラリ確認モーダル -->
    <div id="confirmModal" class="modal-overlay hidden">
        <div class="modal">
            <h2>外部ライブラリの読み込み確認</h2>
            <div class="modal-content">
                <p>このツールを使用するには、以下のJavaScriptライブラリを外部から読み込む必要があります:</p>
                <div class="library-list">
                    <ul>
                        <li><strong>XLSX.js (v0.18.5)</strong> - Excelファイル処理用</li>
                        <li><strong>html2canvas (v1.4.1)</strong> - 画像出力用</li>
                        <li><strong>PapaParse (v5.3.2)</strong> - CSV処理用</li>
                        <li><strong>JSZip (v3.10.1)</strong> - ZIP圧縮用</li>
                        <li><strong>FileSaver.js (v2.0.5)</strong> - ファイル保存用</li>
                        <li><strong>encoding.js (v2.0.0)</strong> - 文字コード変換用</li>
                        <li><strong>Chart.js (v4.4.0)</strong> - グラフ描画用</li>
                    </ul>
                </div>
                <div class="security-info">
                    <strong>接続情報:</strong><br>
                    ・接続先: https://cdnjs.cloudflare.com (Cloudflare公式CDN)<br>
                    ・アップロードしたデータは外部に送信されません<br>
                    ・すべての処理はブラウザ内で完結します
                </div>
                <p style="color: #666; font-size: 13px; margin-top: 15px;">
                    ※ライブラリは毎回のツール起動時に読み込まれ、ブラウザ内でのみ動作します。<br>
                    ※本ツール内で利用されるCDN(Content Delivery Network)経由で提供される外部ライブラリについては、その安全性、可用性、正確性、およびツールの機能に与える影響を含め、一切の責任を負いません。
                </p>
            </div>
            <div class="modal-buttons">
                <button class="btn btn-secondary" id="cancelBtn">キャンセル</button>
                <button class="btn btn-primary" id="approveBtn">記載事項に同意してライブラリを読み込む</button>
            </div>
        </div>
    </div>

    <div id="loadingMessage" class="loading-message hidden">
        <div class="loading-spinner"></div>
        <p>ライブラリを読み込んでいます...</p>
    </div>

    <div id="errorMessage" class="error-message hidden"></div>

    <!-- メインコンテンツ -->
    <div id="mainContent" class="hidden">
        <!-- タブナビゲーション -->
        <div class="tab-navigation">
''')

    # タブボタンを追加
    for i, tool in enumerate(tool_data):
        active = ' active' if i == 0 else ''
        html_parts.append(f'            <div class="tab{active}" onclick="switchTab({i})">{tool["name"]}</div>')

    html_parts.append('        </div>\n')

    # 各ツールのコンテンツを追加
    print("\nコンテンツを統合しています...")
    for i, tool in enumerate(tool_data):
        print(f"  {tool['name']}のコンテンツ...")
        active = ' active' if i == 0 else ''
        html_parts.append(f'        <!-- {tool["name"]} -->')
        html_parts.append(f'        <div id="{tool["id"]}" class="tool-content{active}">')
        cleaned_body = clean_body_content(tool['body'])
        html_parts.append(cleaned_body)
        html_parts.append('        </div>\n')

    html_parts.append('    </div>\n')

    # JavaScript部分
    html_parts.append('''    <script>
        // ========== 共通JavaScript ==========
        const libraries = [
            {
                name: 'XLSX',
                url: 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js',
                check: () => typeof XLSX !== 'undefined'
            },
            {
                name: 'html2canvas',
                url: 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js',
                check: () => typeof html2canvas !== 'undefined'
            },
            {
                name: 'Papa',
                url: 'https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.2/papaparse.min.js',
                check: () => typeof Papa !== 'undefined'
            },
            {
                name: 'JSZip',
                url: 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js',
                check: () => typeof JSZip !== 'undefined'
            },
            {
                name: 'saveAs',
                url: 'https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js',
                check: () => typeof saveAs !== 'undefined'
            },
            {
                name: 'Encoding',
                url: 'https://cdnjs.cloudflare.com/ajax/libs/encoding-japanese/2.0.0/encoding.min.js',
                check: () => typeof Encoding !== 'undefined'
            },
            {
                name: 'Chart',
                url: 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js',
                check: () => typeof Chart !== 'undefined'
            }
        ];

        let librariesLoaded = false;

        // スプラッシュスクリーン表示後、モーダルを表示
        window.addEventListener('load', () => {
            setTimeout(() => {
                document.getElementById('splashScreen').style.display = 'none';
                document.getElementById('confirmModal').classList.remove('hidden');
            }, 2500);
        });

        // ライブラリ読み込み承認
        document.getElementById('approveBtn').addEventListener('click', loadLibraries);
        document.getElementById('cancelBtn').addEventListener('click', handleCancel);

        function loadLibraries() {
            document.getElementById('confirmModal').classList.add('hidden');
            document.getElementById('loadingMessage').classList.remove('hidden');

            const promises = libraries.map(lib => loadScript(lib));

            Promise.all(promises)
                .then(() => {
                    librariesLoaded = true;
                    document.getElementById('loadingMessage').classList.add('hidden');
                    document.getElementById('mainContent').classList.remove('hidden');
                })
                .catch(error => {
                    document.getElementById('loadingMessage').classList.add('hidden');
                    const errorMsg = document.getElementById('errorMessage');
                    errorMsg.textContent = `ライブラリの読み込みに失敗しました: ${error.message}`;
                    errorMsg.classList.remove('hidden');
                });
        }

        function loadScript(lib) {
            return new Promise((resolve, reject) => {
                if (lib.check()) {
                    resolve();
                    return;
                }

                const script = document.createElement('script');
                script.src = lib.url;

                script.onload = () => {
                    if (lib.check()) {
                        console.log(`${lib.name} loaded successfully`);
                        resolve();
                    } else {
                        reject(new Error(`${lib.name} failed to initialize`));
                    }
                };

                script.onerror = () => {
                    reject(new Error(`${lib.name} failed to load from CDN`));
                };

                document.head.appendChild(script);
            });
        }

        function handleCancel() {
            document.getElementById('confirmModal').classList.add('hidden');
            const errorMsg = document.getElementById('errorMessage');
            errorMsg.innerHTML = `
                <strong>ライブラリの読み込みがキャンセルされました</strong><br>
                このツールを使用するには、外部ライブラリの読み込みを承認する必要があります。<br>
                ページを再読み込みして、再度お試しください。
            `;
            errorMsg.classList.remove('hidden');
        }

        // タブ切り替え
        function switchTab(index) {
            // すべてのタブとコンテンツを非アクティブに
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tool-content').forEach(content => content.classList.remove('active'));

            // 選択されたタブとコンテンツをアクティブに
            document.querySelectorAll('.tab')[index].classList.add('active');
            document.querySelectorAll('.tool-content')[index].classList.add('active');
        }
''')

    # 各ツールのJavaScriptを追加（元のJavaScriptをそのまま維持）
    print("\nJavaScriptを統合しています...")
    for tool in tool_data:
        print(f"  {tool['name']}のJavaScript...")
        html_parts.append(f'\n        // ========== {tool["name"]} JavaScript ==========')
        html_parts.append(f'        (function() {{')
        html_parts.append(f'            const toolScope = document.getElementById("{tool["id"]}");')
        html_parts.append(f'            if (!toolScope) return;')

        # JavaScriptコードを追加（スコープ内で実行）
        # document.getElementById を toolScope.querySelector に書き換え
        js_code = tool['scripts']
        # 起動時のスプラッシュスクリーン処理を除去
        js_code = re.sub(
            r'window\.addEventListener\([\'"]load[\'"],[^\}]*\{[^\}]*splashScreen[^\}]*\}[^\)]*\);?',
            '',
            js_code,
            flags=re.DOTALL
        )
        js_code = re.sub(
            r'document\.getElementById\([\'"]splashScreen[\'"]\)[^\;]*;?',
            '',
            js_code
        )
        js_code = re.sub(
            r'document\.getElementById\([\'"]confirmModal[\'"]\)[^\;]*;?',
            '',
            js_code
        )

        html_parts.append(js_code)
        html_parts.append(f'        }})();')

    html_parts.append('''
    </script>
</body>
</html>''')

    # ファイルに書き込み
    print("\nファイルを書き込んでいます...")
    output_path = Path('統合分析ツール.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_parts))

    print(f"\n✓ 統合完了: {output_path}")
    print(f"  ファイルサイズ: {output_path.stat().st_size:,} bytes")
    print(f"  総行数: {len(html_parts):,} 行")

if __name__ == '__main__':
    print("=" * 60)
    print("8つのHTMLツールを統合します")
    print("=" * 60)
    create_integrated_html()
    print("\n" + "=" * 60)
    print("統合完了しました!")
    print("=" * 60)
