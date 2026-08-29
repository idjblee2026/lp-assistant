import os
import re
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import webbrowser

INDEX_FILE = "lp_database.json"

with open(INDEX_FILE, "r", encoding="utf-8") as f:
    database = json.load(f)

HTML_PAGE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>나만의 LP 서재 AI 음악 비서</title>
<style>
    body { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f4f6f8; margin: 0; padding: 20px; color: #333; }
    .container { max-width: 800px; margin: 0 auto; background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); padding: 30px; }
    h1 { text-align: center; color: #1a1a1a; margin-bottom: 25px; font-size: 26px; }
    .search-box { display: flex; gap: 10px; margin-bottom: 25px; }
    input[type="text"] { flex: 1; padding: 14px 18px; font-size: 16px; border: 2px solid #e1e4e8; border-radius: 10px; outline: none; transition: border-color 0.2s; }
    input[type="text"]:focus { border-color: #3b82f6; }
    button { padding: 14px 24px; font-size: 16px; font-weight: bold; background: #1e293b; color: #fff; border: none; border-radius: 10px; cursor: pointer; transition: background 0.2s; }
    button:hover { background: #334155; }
    .quick-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 25px; }
    .tag { background: #f1f5f9; padding: 6px 12px; border-radius: 20px; font-size: 13px; cursor: pointer; color: #475569; transition: all 0.2s; }
    .tag:hover { background: #e2e8f0; color: #0f172a; }
    .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.02); }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .loc-badge { background: #2563eb; color: #fff; font-weight: bold; font-size: 15px; padding: 4px 12px; border-radius: 8px; }
    .album-title { font-size: 18px; font-weight: bold; color: #0f172a; }
    .meta-info { font-size: 14px; color: #64748b; margin-bottom: 10px; }
    .intro-text { font-size: 14px; line-height: 1.6; color: #334155; background: #f8fafc; padding: 12px; border-radius: 8px; }
</style>
</head>
<body>
<div class="container">
    <h1>📀 나만의 LP 서재 AI 음악 비서</h1>
    <div class="search-box">
        <input type="text" id="queryInput" placeholder="분위기, 장르, 가수, 악기 등을 입력하세요 (예: 비 오는 날 듣기 좋은 보컬)">
        <button onclick="doSearch()">검색/추천</button>
    </div>
    <div class="quick-tags">
        <span class="tag" onclick="setQuery('비 오는 날 감성적인 재즈')">🌧️ 비 오는 날 재즈</span>
        <span class="tag" onclick="setQuery('조용한 밤 피아노 연주곡')">🌙 밤 피아노</span>
        <span class="tag" onclick="setQuery('모타운 소울 명반')">🎷 모타운</span>
        <span class="tag" onclick="setQuery('1980년대 신나는 팝')">🎸 80년대 팝</span>
        <span class="tag" onclick="setQuery('웅장한 클래식 교향곡')">🎻 클래식 교향곡</span>
    </div>
    <div id="results"></div>
</div>

<script>
function setQuery(text) {
    document.getElementById('queryInput').value = text;
    doSearch();
}

document.getElementById('queryInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') doSearch();
});

function doSearch() {
    const q = document.getElementById('queryInput').value.trim();
    if (!q) return;
    
    fetch('/search?q=' + encodeURIComponent(q))
        .then(res => res.json())
        .then(data => {
            const resDiv = document.getElementById('results');
            resDiv.innerHTML = '';
            
            if (data.length === 0) {
                resDiv.innerHTML = '<p style="text-align:center; color:#888; padding:30px;">관련된 LP 음반을 찾지 못했습니다.</p>';
                return;
            }
            
            data.forEach(item => {
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <div class="card-header">
                        <span class="album-title">${item.artist} - 《${item.album}》</span>
                        <span class="loc-badge">위치 : ${item.location}</span>
                    </div>
                    <div class="meta-info">
                        ${item.label ? '레이블: ' + item.label + ' | ' : ''}
                        ${item.year ? '발매년도: ' + item.year : ''}
                    </div>
                    <div class="intro-text">${item.intro}</div>
                `;
                resDiv.appendChild(card);
            });
        });
}
</script>
</body>
</html>
"""

def search_lp(query):
    synonyms = {
        "비": ["비", "감성", "서정", "발라드", "비오는", "차분한", "멜로디", "우수"],
        "재즈": ["재즈", "jazz", "색소폰", "트럼펫", "스윙", "마일즈", "콜트레인"],
        "클래식": ["교향곡", "협주곡", "소나타", "오케스트라", "바이올린", "첼로", "필하모닉", "심포니"],
        "조용한": ["어쿠스틱", "피아노", "발라드", "서정", "차분", "밤", "새벽"],
        "모타운": ["motown", "모타운", "소울", "r&b"],
        "비틀즈": ["beatles", "비틀즈", "폴 매카트니", "존 레논", "apple records", "애플 레코드"]
    }
    
    q_words = query.lower().split()
    expanded_words = set(q_words)
    for w in q_words:
        for k, syn_list in synonyms.items():
            if k in w:
                expanded_words.update(syn_list)
                
    results = []
    for item in database:
        score = 0
        text_lower = item["full_text"].lower()
        for w in q_words:
            if w in item["album"].lower(): score += 15
            if w in item["artist"].lower(): score += 15
            if item["label"] and w in item["label"].lower(): score += 10
            if item["year"] and w in item["year"]: score += 10
            if w == item["location"]: score += 50
        for w in expanded_words:
            if w in text_lower:
                score += text_lower.count(w)
        if score > 0:
            results.append((score, item))
            
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results[:7]]

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif parsed_path.path == "/search":
            query_params = urllib.parse.parse_qs(parsed_path.query)
            q = query_params.get('q', [''])[0]
            matched = search_lp(q)
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(matched, ensure_ascii=False).encode('utf-8'))

def run():
    port = 8080
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"웹 음악 비서가 시작되었습니다: http://localhost:{port}")
    webbrowser.open(f"http://localhost:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()