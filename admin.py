import os
import re
import json
import webbrowser
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# build.py의 빌드 기능 가져오기
import build

PORT = 8000
POSTS_DIR = "_posts"
CONFIG_FILE = "config.json"

# -----------------------------------------------------------------
# 로컬 어드민 대시보드 HTML/CSS/JS (Glassmorphism & 미니멀 테마)
# -----------------------------------------------------------------
ADMIN_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Art of Life - 관리자 콘솔</title>
    <style>
        :root {
            --bg-color: #f7f7f5;
            --panel-bg: rgba(255, 255, 255, 0.8);
            --border-color: #dcdcd6;
            --text-color: #2b2b2a;
            --accent-color: #111;
            --accent-hover: #ff8a80;
            --input-bg: #ffffff;
            --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }
        
        .dark-theme {
            --bg-color: #151513;
            --panel-bg: rgba(30, 30, 28, 0.85);
            --border-color: #383835;
            --text-color: #dcdcc6;
            --accent-color: #ffffff;
            --accent-hover: #ff8a80;
            --input-bg: #222220;
            --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            transition: background-color 0.3s, color 0.3s;
        }

        .admin-container {
            max-width: 1000px;
            margin: 0 auto;
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            box-shadow: var(--card-shadow);
            padding: 30px;
            backdrop-filter: blur(10px);
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--accent-color);
            padding-bottom: 15px;
            margin-bottom: 25px;
        }

        h1 {
            margin: 0;
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .header-actions {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        /* 탭 스타일 */
        .tabs {
            display: flex;
            gap: 5px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 25px;
        }

        .tab-btn {
            background: none;
            border: none;
            color: var(--text-color);
            padding: 10px 20px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.95rem;
            border-radius: 4px 4px 0 0;
            opacity: 0.7;
            transition: all 0.2s;
        }

        .tab-btn:hover {
            opacity: 1;
            color: var(--accent-hover);
        }

        .tab-btn.active {
            opacity: 1;
            border: 1px solid var(--border-color);
            border-bottom: 2px solid var(--accent-color);
            background-color: var(--input-bg);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        /* 공통 폼 스타일 */
        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            font-weight: bold;
            font-size: 0.9rem;
            margin-bottom: 6px;
        }

        input[type="text"], input[type="date"], select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid var(--border-color);
            background-color: var(--input-bg);
            color: var(--text-color);
            border-radius: 4px;
            box-sizing: border-box;
            font-family: inherit;
            font-size: 0.95rem;
        }

        textarea {
            resize: vertical;
            min-height: 200px;
        }

        .row-grid {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 15px;
        }

        /* 버튼 스타일 */
        button.btn {
            padding: 10px 18px;
            background-color: var(--accent-color);
            color: var(--bg-color);
            border: 1px solid var(--accent-color);
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }

        button.btn:hover {
            background-color: var(--accent-hover);
            border-color: var(--accent-hover);
            color: #fff;
        }

        button.btn-danger {
            background-color: #ff8a80;
            border-color: #ff8a80;
            color: #fff;
        }

        button.btn-danger:hover {
            background-color: #ff5252;
            border-color: #ff5252;
        }

        /* 글 리스트 테이블 */
        .post-manager {
            display: grid;
            grid-template-columns: 1fr 1.5fr;
            gap: 30px;
        }

        .post-list-panel {
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 15px;
            background-color: var(--input-bg);
            max-height: 550px;
            overflow-y: auto;
        }

        .post-list-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        .post-list-table th, .post-list-table td {
            padding: 10px 8px;
            border-bottom: 1px solid var(--border-color);
            text-align: left;
        }

        .post-list-table tr:hover {
            background-color: rgba(255, 138, 128, 0.1);
            cursor: pointer;
        }

        .editor-panel {
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 20px;
            background-color: var(--input-bg);
        }

        /* 터미널 로그 */
        .terminal-log {
            background-color: #1e1e1e;
            color: #00ff00;
            font-family: monospace;
            padding: 15px;
            border-radius: 6px;
            min-height: 200px;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
            margin-top: 15px;
            font-size: 0.85rem;
        }

        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            background-color: #ccc;
            color: #333;
        }

        .status-success {
            background-color: #d4edda;
            color: #155724;
        }

        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 24px;
            background-color: #333;
            color: #fff;
            border-radius: 4px;
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 1000;
            font-weight: bold;
            font-size: 0.9rem;
        }

        .theme-toggle-btn {
            background: none;
            border: 1px solid var(--border-color);
            padding: 6px 12px;
            cursor: pointer;
            border-radius: 20px;
            color: var(--text-color);
            font-weight: bold;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <div class="admin-container">
        <header>
            <div>
                <h1>Art of Life - 로컬 CMS 대시보드</h1>
                <p style="margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.7;">마크다운 기록과 환경설정을 한 곳에서 편리하게 관리하세요.</p>
            </div>
            <div class="header-actions">
                <button class="theme-toggle-btn" onclick="toggleTheme()">테마 변경</button>
                <button class="btn" onclick="runBuild()">새로고침 빌드</button>
            </div>
        </header>

        <!-- 탭 네비게이션 -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab(event, 'posts')">📝 글 관리 (Posts)</button>
            <button class="tab-btn" onclick="switchTab(event, 'settings')">⚙️ 사이트 환경설정</button>
            <button class="tab-btn" onclick="switchTab(event, 'pages')">📄 홈/소개 편집</button>
            <button class="tab-btn" onclick="switchTab(event, 'deploy')">🚀 깃허브 배포</button>
        </div>

        <!-- 1. 글 관리 콘텐츠 -->
        <div id="tab-posts" class="tab-content active">
            <div class="post-manager">
                <!-- 글 목록 -->
                <div class="post-list-panel">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 15px;">
                        <h3 style="margin:0;">기록물 목록</h3>
                        <button class="btn" style="padding:6px 12px; font-size:0.8rem;" onclick="createNewPost()">새 글 작성</button>
                    </div>
                    <table class="post-list-table">
                        <thead>
                            <tr>
                                <th>날짜</th>
                                <th>카테고리</th>
                                <th>제목</th>
                            </tr>
                        </thead>
                        <tbody id="post-list-tbody">
                            <!-- 로딩된 목록이 추가됩니다 -->
                        </tbody>
                    </table>
                </div>

                <!-- 글 편집기 -->
                <div class="editor-panel">
                    <h3 id="editor-title" style="margin-top:0; margin-bottom: 15px; border-bottom: 1px dotted var(--border-color); padding-bottom: 10px;">새 글 작성</h3>
                    <form id="post-form" onsubmit="savePost(event)">
                        <input type="hidden" id="post-filename" value="">
                        
                        <div class="form-group">
                            <label for="post-title">제목</label>
                            <input type="text" id="post-title" required placeholder="글 제목을 적어주세요">
                        </div>

                        <div class="row-grid">
                            <div class="form-group">
                                <label for="post-category">분류</label>
                                <select id="post-category">
                                    <option value="일기장">일기장</option>
                                    <option value="Notes">Notes</option>
                                    <option value="Projects">Projects</option>
                                    <option value="사색 일지">사색 일지</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="post-date">날짜</label>
                                <input type="date" id="post-date" required>
                            </div>
                            <div class="form-group" style="display:flex; align-items:flex-end; padding-bottom:1px;">
                                <span style="font-size:0.8rem; opacity:0.6; font-family:monospace;" id="file-indicator">신규 파일</span>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="post-body">본문 내용 (Markdown 문법 지원)</label>
                            <textarea id="post-body" required placeholder="여기에 본문 내용을 작성해 주세요."></textarea>
                        </div>

                        <div style="display:flex; justify-content:space-between; margin-top: 20px;">
                            <button type="submit" class="btn">기록 저장</button>
                            <button type="button" id="delete-btn" class="btn btn-danger" style="display:none;" onclick="deletePost()">글 삭제</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- 2. 환경설정 콘텐츠 -->
        <div id="tab-settings" class="tab-content">
            <div class="editor-panel" style="max-width: 600px; margin: 0 auto;">
                <h3 style="margin-top:0; margin-bottom:20px; border-bottom: 1px dotted var(--border-color); padding-bottom: 10px;">사이트 전역 설정</h3>
                <form onsubmit="saveSettings(event)">
                    <div class="form-group">
                        <label for="setting-title">웹사이트 브랜드/제목</label>
                        <input type="text" id="setting-title" required>
                    </div>
                    <div class="form-group">
                        <label for="setting-description">사이드바 한 줄 요약/설명</label>
                        <input type="text" id="setting-description" required>
                    </div>
                    <div class="form-group">
                        <label for="setting-favicon">파비콘 경로 (favicon.png 등)</label>
                        <input type="text" id="setting-favicon" required>
                    </div>
                    <div class="form-group">
                        <label for="setting-domain">깃허브 Pages 도메인 주소</label>
                        <input type="text" id="setting-domain" required>
                    </div>
                    <div class="form-group">
                        <label for="setting-email">Contact 이메일</label>
                        <input type="text" id="setting-email" required>
                    </div>
                    <div class="form-group">
                        <label for="setting-github">Contact 깃허브 주소</label>
                        <input type="text" id="setting-github" required>
                    </div>
                    <div style="margin-top:25px; text-align:right;">
                        <button type="submit" class="btn">설정 저장 및 일괄 반영</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- 3. 페이지 편집 콘텐츠 -->
        <div id="tab-pages" class="tab-content">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:25px;">
                <div class="editor-panel">
                    <h3 style="margin-top:0;">홈 페이지 본문 편집 (index.html)</h3>
                    <div class="form-group">
                        <label for="page-index-body">HTML 구조 편집</label>
                        <textarea id="page-index-body" style="min-height: 450px; font-family:monospace; font-size:0.85rem;"></textarea>
                    </div>
                    <div style="text-align:right;">
                        <button class="btn" onclick="savePageContent('index')">홈 본문 저장</button>
                    </div>
                </div>

                <div class="editor-panel">
                    <h3 style="margin-top:0;">소개 페이지 본문 편집 (about.html)</h3>
                    <div class="form-group">
                        <label for="page-about-body">HTML 구조 편집</label>
                        <textarea id="page-about-body" style="min-height: 450px; font-family:monospace; font-size:0.85rem;"></textarea>
                    </div>
                    <div style="text-align:right;">
                        <button class="btn" onclick="savePageContent('about')">소개 본문 저장</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 4. 배포 콘텐츠 -->
        <div id="tab-deploy" class="tab-content">
            <div class="editor-panel" style="max-width: 700px; margin: 0 auto;">
                <h3 style="margin-top:0;">깃허브 Pages로 라이브 배포</h3>
                <p>로컬에서 수정한 글과 설정 파일들을 깃허브 원격 저장소로 즉시 커밋 및 푸시하여 웹에 라이브로 게시합니다.</p>
                <div style="margin: 20px 0;">
                    <button class="btn" onclick="deployToGitHub()" id="deploy-btn" style="padding:12px 24px; font-size:1.05rem;">원클릭 깃허브 배포 실행</button>
                </div>
                <label style="font-weight:bold; font-size:0.9rem;">터미널 배포 프로세스 출력 로그:</label>
                <div id="terminal-output" class="terminal-log">배포를 기다리는 중...</div>
            </div>
        </div>
    </div>

    <div id="toast" class="toast">저장 완료!</div>

    <script>
        // 전역 상태
        let configData = {};

        function toggleTheme() {
            document.body.classList.toggle('dark-theme');
            const isDark = document.body.classList.contains('dark-theme');
            localStorage.setItem('admin-dark-theme', isDark);
        }

        // 탭 전환
        function switchTab(evt, tabName) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            // 활성화
            if (evt && evt.currentTarget) {
                evt.currentTarget.classList.add('active');
            } else if (window.event && window.event.srcElement) {
                // IE/Legacy fallback
                window.event.srcElement.classList.add('active');
            }
            document.getElementById(`tab-${tabName}`).classList.add('active');

            if (tabName === 'posts') {
                loadPosts();
            } else if (tabName === 'settings' || tabName === 'pages') {
                loadConfig();
            }
        }

        // 토스트 출력
        function showToast(msg) {
            const toast = document.getElementById("toast");
            toast.textContent = msg;
            toast.style.opacity = 1;
            setTimeout(() => {
                toast.style.opacity = 0;
            }, 2500);
        }

        // 날짜 기본값 채우기
        function setDefaultDate() {
            const today = new Date().toISOString().substring(0, 10);
            document.getElementById("post-date").value = today;
        }

        // 글 목록 로드
        function loadPosts() {
            fetch('/api/list-posts')
                .then(res => res.json())
                .then(data => {
                    const tbody = document.getElementById("post-list-tbody");
                    tbody.innerHTML = "";
                    
                    data.sort((a,b) => new Date(b.date) - new Date(a.date));

                    data.forEach(post => {
                        const tr = document.createElement("tr");
                        tr.innerHTML = `
                            <td style="color:#777;">${post.date}</td>
                            <td><span class="status-badge">${post.category}</span></td>
                            <td style="font-weight:bold;">${post.title}</td>
                        `;
                        tr.addEventListener("click", () => selectPost(post.filename));
                        tbody.appendChild(tr);
                    });
                });
        }

        // 특정 글 선택 로드
        function selectPost(filename) {
            fetch(`/api/get-post?file=${encodeURIComponent(filename)}`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById("editor-title").textContent = "글 수정 및 상세 편집";
                    document.getElementById("post-filename").value = filename;
                    document.getElementById("post-title").value = data.title;
                    document.getElementById("post-category").value = data.category;
                    document.getElementById("post-date").value = data.date;
                    document.getElementById("post-body").value = data.body;
                    document.getElementById("file-indicator").textContent = filename;
                    document.getElementById("delete-btn").style.display = "block";
                });
        }

        // 새 글 폼 초기화
        function createNewPost() {
            document.getElementById("editor-title").textContent = "새 글 작성";
            document.getElementById("post-filename").value = "";
            document.getElementById("post-title").value = "";
            document.getElementById("post-category").value = "일기장";
            setDefaultDate();
            document.getElementById("post-body").value = "";
            document.getElementById("file-indicator").textContent = "신규 파일";
            document.getElementById("delete-btn").style.display = "none";
        }

        // 글 저장
        function savePost(event) {
            event.preventDefault();
            
            const postData = {
                filename: document.getElementById("post-filename").value,
                title: document.getElementById("post-title").value,
                category: document.getElementById("post-category").value,
                date: document.getElementById("post-date").value,
                body: document.getElementById("post-body").value
            };

            fetch('/api/save-post', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(postData)
            })
            .then(res => res.json())
            .then(res => {
                if (res.status === "success") {
                    showToast("기록 저장 및 리빌드 완료!");
                    loadPosts();
                    selectPost(res.filename); // 저장 후 로드 상태 유지
                } else {
                    alert("저장에 실패했습니다: " + res.message);
                }
            });
        }

        // 글 삭제
        function deletePost() {
            const filename = document.getElementById("post-filename").value;
            if (!filename) return;

            if (confirm(`진짜로 이 글(${filename})을 홈페이지에서 영구 삭제하시겠습니까?`)) {
                fetch('/api/delete-post', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename })
                })
                .then(res => res.json())
                .then(res => {
                    if (res.status === "success") {
                        showToast("정상적으로 삭제 및 리빌드되었습니다.");
                        createNewPost();
                        loadPosts();
                    } else {
                        alert("삭제에 실패했습니다: " + res.message);
                    }
                });
            }
        }

        // 환경설정 로드
        function loadConfig() {
            fetch('/api/get-config')
                .then(res => res.json())
                .then(data => {
                    configData = data;
                    
                    // 설정 탭 폼 매핑
                    const titleEl = document.getElementById("setting-title");
                    if (titleEl) titleEl.value = data.site_title || "";
                    const descEl = document.getElementById("setting-description");
                    if (descEl) descEl.value = data.site_description || "";
                    const favEl = document.getElementById("setting-favicon");
                    if (favEl) favEl.value = data.favicon_path || "";
                    const domEl = document.getElementById("setting-domain");
                    if (domEl) domEl.value = data.site_domain || "";
                    const mailEl = document.getElementById("setting-email");
                    if (mailEl) mailEl.value = data.contact_email || "";
                    const gitEl = document.getElementById("setting-github");
                    if (gitEl) gitEl.value = data.contact_github || "";

                    // 페이지 편집 탭 폼 매핑
                    const idxBody = document.getElementById("page-index-body");
                    if (idxBody) idxBody.value = data.index_body || "";
                    const abBody = document.getElementById("page-about-body");
                    if (abBody) abBody.value = data.about_body || "";
                });
        }

        // 환경설정 저장
        function saveSettings(event) {
            event.preventDefault();
            
            const updatedConfig = {
                ...configData,
                site_title: document.getElementById("setting-title").value,
                site_description: document.getElementById("setting-description").value,
                favicon_path: document.getElementById("setting-favicon").value,
                site_domain: document.getElementById("setting-domain").value,
                contact_email: document.getElementById("setting-email").value,
                contact_github: document.getElementById("setting-github").value
            };

            fetch('/api/save-config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedConfig)
            })
            .then(res => res.json())
            .then(res => {
                if (res.status === "success") {
                    showToast("설정 저장 및 일괄 갱신 완료!");
                    loadConfig();
                } else {
                    alert("설정 저장 실패: " + res.message);
                }
            });
        }

        // 홈/소개 본문 저장
        function savePageContent(pageKey) {
            const textareaId = `page-${pageKey}-body`;
            const content = document.getElementById(textareaId).value;

            const updatedConfig = {
                ...configData,
                [`${pageKey}_body`]: content
            };

            fetch('/api/save-config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedConfig)
            })
            .then(res => res.json())
            .then(res => {
                if (res.status === "success") {
                    showToast(`${pageKey === 'index' ? '홈' : '소개'} 페이지 본문 저장 및 갱신 성공!`);
                    loadConfig();
                } else {
                    alert("페이지 본문 저장 실패: " + res.message);
                }
            });
        }

        // 사이트 빌더 즉시 실행 요청
        function runBuild() {
            fetch('/api/run-build', { method: 'POST' })
                .then(res => res.json())
                .then(res => {
                    if (res.status === "success") {
                        showToast("로컬 빌드 성공!");
                    } else {
                        alert("빌드 실패: " + res.message);
                    }
                });
        }

        // 깃허브 배포 요청
        function deployToGitHub() {
            const btn = document.getElementById("deploy-btn");
            const output = document.getElementById("terminal-output");
            
            btn.disabled = true;
            btn.textContent = "배포 중...";
            output.textContent = "[Info] 깃허브 배포 프로세스를 개시합니다. 잠시만 대기해 주세요...\\n";

            fetch('/api/git-deploy', { method: 'POST' })
                .then(res => res.json())
                .then(res => {
                    btn.disabled = false;
                    btn.textContent = "원클릭 깃허브 배포 실행";
                    
                    output.textContent += `\\n[Git Output]\\n${res.message}\\n`;
                    if (res.status === "success") {
                        output.textContent += "\\n[Success] 배포가 성공했습니다! 깃허브 Actions 가동을 시작합니다.";
                        showToast("깃허브 푸시 성공!");
                    } else {
                        output.textContent += "\\n[Error] 배포 과정 중 에러가 발생했습니다.";
                        alert("깃허브 배포 실패. 터미널 로그를 확인하세요.");
                    }
                })
                .catch(err => {
                    btn.disabled = false;
                    btn.textContent = "원클릭 깃허브 배포 실행";
                    output.textContent += `\\n[Network Error] 서버 연결에 실패했습니다: ${err}`;
                });
        }

        // 페이지 로딩 시 초기 셋업
        document.addEventListener("DOMContentLoaded", () => {
            // 저장된 관리자 테마 복구
            const isDark = localStorage.getItem('admin-dark-theme') === 'true';
            if (isDark) {
                document.body.classList.add('dark-theme');
            }

            setDefaultDate();
            loadPosts();
            loadConfig();
        });
    </script>
</body>
</html>
"""

# BaseHTTPRequestHandler를 상속받은 CMS 제어 클래스
class CMSRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        
        # 1. 메인 관리자 대시보드 뷰
        if parsed_url.path == "/" or parsed_url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(ADMIN_HTML.encode("utf-8"))
            return

        # 2. API: 포스트 목록 조회
        elif parsed_url.path == "/api/list-posts":
            posts = []
            if os.path.exists(POSTS_DIR):
                for filename in os.listdir(POSTS_DIR):
                    if filename.endswith(".md"):
                        filepath = os.path.join(POSTS_DIR, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            raw = f.read()
                        
                        # 간단 프론트매터 파싱
                        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', raw, re.DOTALL)
                        if match:
                            meta_raw = match.group(1)
                            meta = {}
                            for line in meta_raw.split('\n'):
                                if ':' in line:
                                    k, v = line.split(':', 1)
                                    meta[k.strip()] = v.strip()
                            
                            posts.append({
                                "filename": filename,
                                "title": meta.get("title", "무제"),
                                "category": meta.get("category", "일기장"),
                                "date": meta.get("date", "")
                            })
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(posts, ensure_ascii=False).encode("utf-8"))
            return

        # 3. API: 단일 포스트 본문 조회
        elif parsed_url.path == "/api/get-post":
            query = parse_qs(parsed_url.query)
            filename = query.get("file", [""])[0]
            
            if not filename:
                self.send_error_json(400, "파일명이 지정되지 않았습니다.")
                return
                
            filepath = os.path.join(POSTS_DIR, filename)
            if not os.path.exists(filepath):
                self.send_error_json(404, "포스트를 찾을 수 없습니다.")
                return

            with open(filepath, 'r', encoding='utf-8') as f:
                raw = f.read()

            match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw, re.DOTALL)
            title, category, date, body = "무제", "일기장", "", ""
            if match:
                meta_raw = match.group(1)
                body = match.group(2).strip()
                meta = {}
                for line in meta_raw.split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        meta[k.strip()] = v.strip()
                
                title = meta.get("title", "무제")
                category = meta.get("category", "일기장")
                date = meta.get("date", "")

            response_data = {
                "title": title,
                "category": category,
                "date": date,
                "body": body
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
            return

        # 4. API: config.json 조회
        elif parsed_url.path == "/api/get-config":
            config_data = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(config_data, ensure_ascii=False).encode("utf-8"))
            return

        # 404 리턴
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed_url = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b""
        
        data = {}
        if content_length > 0:
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception:
                # 본문 바디가 필수적이지 않은 API 요청에 대한 무해한 예외 통과
                pass

        # 1. API: 포스트 저장
        if parsed_url.path == "/api/save-post":
            filename = data.get("filename", "")
            title = data.get("title", "").strip()
            category = data.get("category", "일기장").strip()
            date = data.get("date", "").strip()
            body = data.get("body", "").strip()

            if not title or not date or not body:
                self.send_error_json(400, "필수 항목(제목, 날짜, 본문)이 누락되었습니다.")
                return

            # 파일명이 없으면 날짜와 안전한 문자열을 조립해 고유 명칭 부여
            if not filename:
                safe_title = re.sub(r'[^a-zA-Z0-9가-힣_-]', '', title)[:20]
                filename = f"{date}-{safe_title}.md"

            filepath = os.path.join(POSTS_DIR, filename)
            
            # 마크다운 YAML 포맷 조립
            md_content = f"""---
title: {title}
category: {category}
date: {date}
---
{body}
"""
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)

            # 저장 완료 후 즉시 정적 웹사이트 컴파일 리빌드 구동
            try:
                build.build_site()
                self.send_success_json({"filename": filename})
            except Exception as e:
                self.send_error_json(500, f"저장은 되었으나 사이트 빌드 중 에러가 났습니다: {str(e)}")
            return

        # 2. API: 포스트 삭제
        elif parsed_url.path == "/api/delete-post":
            filename = data.get("filename", "")
            if not filename:
                self.send_error_json(400, "삭제할 파일명이 제공되지 않았습니다.")
                return

            filepath = os.path.join(POSTS_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # 컴파일 생성되었던 HTML 파일도 함께 자동 삭제
            target_folder = build.CATEGORY_MAP.get(build.parse_markdown_to_html) # build.py의 카테고리 로직 활용
            # 간단하게 HTML 경로 유추
            # build.py 스캔 후 다시 리빌드하면 sitemap.xml 등에서 안전하게 소멸
            html_filename = filename.replace('.md', '.html')
            for folder in build.CATEGORY_MAP.values():
                html_path = os.path.join(folder, html_filename)
                if os.path.exists(html_path):
                    os.remove(html_path)

            try:
                build.build_site()
                self.send_success_json({})
            except Exception as e:
                self.send_error_json(500, f"삭제는 되었으나 리빌드 중 오류가 났습니다: {str(e)}")
            return

        # 3. API: config.json 설정 저장
        elif parsed_url.path == "/api/save-config":
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            # 설정 즉각 일괄 반영 리빌드 구동
            try:
                build.build_site()
                self.send_success_json({})
            except Exception as e:
                self.send_error_json(500, f"설정은 변경되었으나 사이트 빌딩 중 오류: {str(e)}")
            return

        # 4. API: 즉시 로컬 리빌더 수동 실행
        elif parsed_url.path == "/api/run-build":
            try:
                build.build_site()
                self.send_success_json({})
            except Exception as e:
                self.send_error_json(500, f"리빌드 실패: {str(e)}")
            return

        # 5. API: 깃허브 배포 (Subprocess 대리 push)
        elif parsed_url.path == "/api/git-deploy":
            try:
                # 1. git add .
                add_res = subprocess.run(["git", "add", "."], capture_output=True, text=True, check=True)
                
                # 2. git commit -m
                # 변경사항이 없을 때의 커밋 실패 예외 처리
                try:
                    commit_res = subprocess.run(
                        ["git", "commit", "-m", "site update via CMS Dashboard"],
                        capture_output=True, text=True, check=True
                    )
                    commit_output = commit_res.stdout + commit_res.stderr
                except subprocess.CalledProcessError as ce:
                    # 변경사항이 없으면 exit code 1을 리턴하므로 이 경우는 통과 처리
                    if "nothing to commit" in ce.stdout or "nothing to commit" in ce.stderr or "clean" in ce.stdout:
                        commit_output = "변경 사항이 없어 커밋을 스킵합니다.\n"
                    else:
                        raise ce
                
                # 3. git push origin main
                push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, check=True)
                
                total_output = f"[Add Output]\n{add_res.stdout}\n[Commit Output]\n{commit_output}\n[Push Output]\n{push_res.stdout}\n{push_res.stderr}"
                
                self.send_success_json({"message": total_output})
            except subprocess.CalledProcessError as e:
                error_msg = f"Git 실행 에러 발생:\nStdout: {e.stdout}\nStderr: {e.stderr}"
                self.send_error_json(500, error_msg)
            except Exception as ex:
                self.send_error_json(500, f"알 수 없는 시스템 오류: {str(ex)}")
            return

        self.send_response(404)
        self.end_headers()

    # 편의 헬퍼: 에러 JSON 전송
    def send_error_json(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "error", "message": message}, ensure_ascii=False).encode("utf-8"))

    # 편의 헬퍼: 성공 JSON 전송
    def send_success_json(self, extra_dict):
        response = {"status": "success"}
        response.update(extra_dict)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))


def start_server():
    server = HTTPServer(("localhost", PORT), CMSRequestHandler)
    print(f"[CMS Server] 로컬 대시보드 서버가 http://localhost:{PORT} 에서 정상 가동 중입니다.")
    print("종료하려면 터미널 창에서 Ctrl + C를 누르세요.")
    
    # 자동으로 브라우저 띄워 어드민 콘솔로 연결
    webbrowser.open(f"http://localhost:{PORT}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[CMS Server] 서버를 안전하게 종료했습니다.")


if __name__ == "__main__":
    start_server()
