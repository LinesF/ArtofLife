import os
import re
import json
from datetime import datetime

# 4가지 카테고리 한글명 및 영문 폴더 매핑
CATEGORY_MAP = {
    "일기장": "diary",
    "Notes": "notes",
    "Projects": "projects",
    "사색 일지": "thought-log"
}

# 깃허브 Pages 퍼블리시 도메인 명시
SITE_DOMAIN = "https://linesf.github.io/ArtofLife"

# -----------------------------------------------------------------
# 단일 공통 HTML 레이아웃 래퍼 함수 (파비콘 및 공통 구조 일괄 제어)
# -----------------------------------------------------------------
def render_html_layout(title, content, depth=0, description=""):
    # depth에 따른 상대경로 셋팅
    rel = "../" * depth
    
    # 3대 테마(Light, Sepia, Dark), 파비콘, 모바일 토글 텍스트 버튼이 내장된 완성도 높은 템플릿
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description if description else title + ' - Art of Life'}">
    <title>{title} - Art of Life</title>
    <link rel="stylesheet" href="{rel}style.css">
    <link rel="icon" type="image/png" href="{rel}favicon.png">
    <script src="{rel}theme.js"></script>
</head>
<body>
    <div class="container">
        <!-- 왼쪽 사이드바 네비게이션 -->
        <nav class="sidebar" aria-label="메인 메뉴">
            <div class="site-title">
                <a id="nav-brand" href="{rel}index.html">Art of Life</a>
            </div>
            
            <button id="menu-toggle" class="menu-toggle-btn">Menu ☰</button>

            <div class="sidebar-content">
                <div class="about-section">
                    <h2><a id="nav-about-sidebar" href="{rel}about.html">About</a></h2>
                    <p>일상의 소소한 이야기와 개인적인 관심사를 가볍고 편안하게 기록하는 개인 정원입니다.</p>
                </div>

                <h2>분류 <a id="search-trigger" href="{rel}search.html" style="font-size: 1rem; text-decoration: none; margin-left: 5px;">🔍</a></h2>
                <ul>
                    <li><a id="nav-diary" href="{rel}diary/index.html">📖 일기장</a></li>
                    <li><a id="nav-notes" href="{rel}notes/index.html">📝 Notes</a></li>
                    <li><a id="nav-projects" href="{rel}projects/index.html">💻 Projects</a></li>
                    <li><a id="nav-thoughts" href="{rel}thought-log/index.html">🧠 사색 일지</a></li>
                </ul>

                <h2>Theme</h2>
                <div style="font-family: monospace; font-size: 0.85rem; display: flex; gap: 10px; margin-bottom: 20px;">
                    <a id="theme-light" class="theme-link" href="#" onclick="setTheme('light'); return false;">Light</a>
                    <a id="theme-sepia" class="theme-link" href="#" onclick="setTheme('sepia'); return false;">Sepia</a>
                    <a id="theme-dark" class="theme-link" href="#" onclick="setTheme('dark'); return false;">Dark</a>
                </div>

                <h2>Contact</h2>
                <ul class="contact-list">
                    <li>Email: <a id="contact-email" href="mailto:your-email@example.com">email@example.com</a></li>
                    <li>GitHub: <a id="contact-github" href="https://github.com/your-username" target="_blank">github.com/username</a></li>
                </ul>
            </div>
        </nav>

        <!-- 오른쪽 본문 콘텐츠 -->
        <main class="content">
            {content}
            <footer>
                <p>© 2026 Art of Life. Built with pure HTML & CSS.</p>
            </footer>
        </main>
    </div>
</body>
</html>
"""
    return html

# -----------------------------------------------------------------
# 1. 인덱스(index.html) 정적 바디 콘텐츠 정의
# -----------------------------------------------------------------
INDEX_BODY = """<header>
    <h1>일상의 기록</h1>
    <p>오래된 종이책을 읽듯, 조용하고 차분하게 생각을 나누는 정원입니다.</p>
</header>

<article>
    <div class="intro-box">
        <p>환영합니다. 이곳은 저의 소소한 일상, 관심사, 흘러가는 생각들을 차분히 적어두는 개인 홈페이지입니다.</p>
        <p>화려한 장식이나 복잡한 기능 없이, 오직 텍스트와 단순한 구조로만 구성된 클래식한 공간입니다. 지나치게 빠르고 시끄러운 인터넷 세상 속에서 잠시 쉬어가는 마음으로 글을 쓰고 정리하고 있습니다.</p>
    </div>
    
    <h2>최근 관심사</h2>
    <ul>
        <li><strong>일상 일기</strong>: 하루 동안 겪었던 소소한 이야기나 감정들</li>
        <li><strong>관심사 아카이브</strong>: 독서, 음악, 그리고 프로그래밍 등 요즘 깊게 들여다보고 있는 것들에 대한 생각</li>
        <li><strong>사색 단상</strong>: 길을 걷다 문득 든 생각이나 짧은 메모들</li>
    </ul>
    
    <blockquote>
        "단순함은 궁극의 정교함이다." <br>
        — 레오나르도 다빈치
    </blockquote>
</article>
"""

# -----------------------------------------------------------------
# 2. 자기소개(about.html) 정적 바디 콘텐츠 정의
# -----------------------------------------------------------------
ABOUT_BODY = """<header>
    <h1>자기소개 (About Me)</h1>
    <p>단순하고 명료한 아날로그의 가치를 지향합니다.</p>
</header>

<article>
    <figure style="float: right; margin: 0 0 20px 20px; width: 220px; text-align: center; font-family: monospace; font-size: 0.8rem; color: #666;">
        <img src="about/classic_desk.png" alt="클래식 책상 책화" style="width: 100%; border: 1px solid #aaa; padding: 3px; background-color: #fff;">
        <figcaption>필름 톤으로 렌더링된 책상 삽화</figcaption>
    </figure>

    <p>안녕하세요. 이곳은 저의 소소한 생각들과 하루하루의 일상, 그리고 깊어가는 관심사들을 모아두는 정적 웹사이트입니다. 화려한 장식 없이 단순한 텍스트로 가득 찬 이 공간처럼, 저 역시 본질적이고 명료한 것을 좋아합니다.</p>

    <h2>역할 및 관심사</h2>
    <ul>
        <li><strong>역할</strong>: 소프트웨어 엔지니어 / 테크니컬 라이터</li>
        <li><strong>관심사</strong>: 웹 표준, 정적 사이트 아키텍처, 정보 설계, 미니멀리즘</li>
        <li><strong>좋아하는 것</strong>: 차분한 음악 듣기, 책 읽기, 사소한 일상의 기록, 조용한 산책</li>
    </ul>

    <h2>나의 가치관</h2>
    <ul>
        <li><strong>덜어내는 삶</strong>: 불필요한 노이즈와 치장을 배제하고 본질에 집중합니다.</li>
        <li><strong>꾸준한 아카이빙</strong>: 거창한 결과물보다 매일의 작은 생각을 쌓는 시간이 중요합니다.</li>
        <li><strong>자신만의 속도</strong>: 인터넷 세상의 빠른 유행에 휩쓸리지 않고 차분한 아날로그 템포를 지향합니다.</li>
    </ul>

    <h2>커리어 & 기술 스택</h2>
    <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-family: monospace; font-size: 0.9rem;">
        <thead>
            <tr style="border-bottom: 2px solid #333; text-align: left;">
                <th style="padding: 6px 0;">기간</th>
                <th style="padding: 6px 0;">소속 및 프로젝트</th>
                <th style="padding: 6px 0;">주요 내용</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 6px 0;">2024.03 - 현재</td>
                <td style="padding: 6px 0;">개인 프로젝트 & 프리랜서</td>
                <td style="padding: 6px 0;">정적 웹 빌더 개발, 타이포그래피 연구</td>
            </tr>
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 6px 0;">2021.01 - 2024.02</td>
                <td style="padding: 6px 0;">클라우드 솔루션사</td>
                <td style="padding: 6px 0;">주니어 웹 개발자, UI/UX 접근성 개선</td>
            </tr>
        </tbody>
    </table>

    <h2>연혁 (Timeline)</h2>
    <ul style="list-style-type: none; padding-left: 0; font-family: monospace;">
        <li style="margin-bottom: 10px; border-left: 2px solid #ccc; padding-left: 15px;">
            <strong>2026년 7월</strong>: 개인 정적 홈페이지 개설 및 운영 시스템 완비
        </li>
        <li style="margin-bottom: 10px; border-left: 2px solid #ccc; padding-left: 15px;">
            <strong>2024년 3월</strong>: 정적 웹 기술과 미니멀 인터페이스 디자인 독립 학습 개시
        </li>
        <li style="margin-bottom: 10px; border-left: 2px solid #ccc; padding-left: 15px;">
            <strong>2021년 1월</strong>: 소프트웨어 프로그래밍 첫 입문
        </li>
        <li style="margin-bottom: 10px; border-left: 2px solid #ccc; padding-left: 15px;">
            <strong>2018년 9월</strong>: 기록하고 아카이빙하는 사색 글쓰기 습관 시작
        </li>
    </ul>

    <h2>사용하는 장비 (Hardware & Software)</h2>
    <ul>
        <li><strong>하드웨어</strong>: 맥북 에어(MacBook Air), HHKB Professional Classic 키보드, 몰스킨 플레인 노트</li>
        <li><strong>소프트웨어</strong>: VS Code, Vim 에디터, Obsidian (옵시디언), Firefox 개발자 에디션</li>
        <li><strong>기타</strong>: 드립 커피 (예가체프 아이스), 차가운 우롱차</li>
    </ul>
</article>
"""

# -----------------------------------------------------------------
# 3. 검색(search.html) 정적 바디 콘텐츠 및 스크립트 정의
# -----------------------------------------------------------------
SEARCH_BODY = """<header>
    <h1>통합 검색 (Search)</h1>
    <p>단어 코사인 유사도 분석을 통해 본문 내용을 검색합니다. 카테고리와 연도로 결과를 필터링해 보세요.</p>
</header>

<article class="search-container">
    <!-- 검색 인풋 영역 -->
    <div class="search-input-wrapper">
        <input type="text" id="search-input" placeholder="검색어 또는 문장을 입력해 보세요 (예: 정적 웹, 가치관)..." aria-label="검색어 입력">
        <button id="search-btn">검색</button>
    </div>

    <!-- 필터 패널 영역 (연도 필터를 더블 레인지 슬라이더로 변경) -->
    <div class="search-filters">
        <div class="filter-group">
            <span class="filter-group-title">분류 필터</span>
            <label class="filter-label"><input type="checkbox" class="filter-category" value="일기장" checked> 일기장</label>
            <label class="filter-label"><input type="checkbox" class="filter-category" value="Notes" checked> Notes</label>
            <label class="filter-label"><input type="checkbox" class="filter-category" value="Projects" checked> Projects</label>
            <label class="filter-label"><input type="checkbox" class="filter-category" value="사색 일지" checked> 사색 일지</label>
            <label class="filter-label"><input type="checkbox" class="filter-category" value="소개" checked> 소개문</label>
        </div>
        <div class="filter-group" style="margin-top: 10px; border-top: 1px dotted #eee; padding-top: 10px;">
            <span class="filter-group-title">연도 필터</span>
            <div class="range-slider-container">
                <div class="slider-track" id="slider-track"></div>
                <input type="range" id="slider-min" min="2024" max="2026" value="2024" step="1" aria-label="시작 연도">
                <input type="range" id="slider-max" min="2024" max="2026" value="2026" step="1" aria-label="종료 연도">
            </div>
            <span id="range-value-display" style="font-family: monospace; font-size: 0.9rem; margin-left: 15px; font-weight: bold; color: #222;">2024년 ~ 2026년</span>
        </div>
    </div>

    <!-- 검색 정보 바 -->
    <div id="search-meta-bar" style="font-family: monospace; font-size: 0.9rem; color: #555; border-bottom: 1px solid #aaa; padding-bottom: 8px; margin-bottom: 15px;">
        검색어를 입력해 주세요.
    </div>

    <!-- 검색 결과 리스트 -->
    <div id="search-results" class="search-results-list">
        <!-- JS에 의해 동적으로 검색 결과 렌더링 -->
    </div>

    <!-- 페이지네이션 하단 영역 -->
    <div id="pagination-wrapper" class="pagination-wrapper">
        <!-- JS에 의해 동적으로 페이지 번호 생성 -->
    </div>
</article>

<!-- 검색엔진 코사인 유사도 분석 스크립트 -->
<script>
    // 로컬 file:// 보안 에러(CORS) 방지를 위해 검색 DB를 인라인 변수로 정의
    const SEARCH_DATA = /*DATA_START*/[]/*DATA_END*/;

    document.addEventListener("DOMContentLoaded", () => {
        const searchInput = document.getElementById("search-input");
        const searchBtn = document.getElementById("search-btn");
        const resultsContainer = document.getElementById("search-results");
        const paginationWrapper = document.getElementById("pagination-wrapper");
        const metaBar = document.getElementById("search-meta-bar");

        // 더블 슬라이더 노드 수집
        const sliderMin = document.getElementById("slider-min");
        const sliderMax = document.getElementById("slider-max");
        const sliderTrack = document.getElementById("slider-track");
        const rangeDisplay = document.getElementById("range-value-display");

        // 게시글 데이터로부터 동적으로 연도 범위(최소/최대) 산출
        const years = SEARCH_DATA.map(d => parseInt(d.date.substring(0, 4))).filter(y => !isNaN(y));
        let minLimit = years.length > 0 ? Math.min(...years) : 2026;
        let maxLimit = years.length > 0 ? Math.max(...years) : 2026;

        // 최소 1년 기준의 조작 범위를 보장 (최소/최대 연도가 같은 경우 예외 보정)
        if (minLimit === maxLimit) {
            minLimit = maxLimit - 1;
        }

        // 슬라이더 요소의 작동 한계 설정 갱신
        sliderMin.min = minLimit;
        sliderMin.max = maxLimit;
        sliderMin.value = minLimit;
        
        sliderMax.min = minLimit;
        sliderMax.max = maxLimit;
        sliderMax.value = maxLimit;

        const ITEMS_PER_PAGE = 3; 
        let currentPage = 1;
        let currentFilteredResults = [];

        // 1. 더블 레인지 슬라이더 트랙 동적 업데이트 함수 (충돌 제어는 이벤트 리스너에서 직접 개별 처리)
        function updateSliderTrack() {
            const minVal = parseInt(sliderMin.value);
            const maxVal = parseInt(sliderMax.value);

            // 진행바 그라데이션 채색 비율 산출
            const minPercent = ((minVal - minLimit) / (maxLimit - minLimit)) * 100;
            const maxPercent = ((maxVal - minLimit) / (maxLimit - minLimit)) * 100;
            
            // 선택된 안쪽 공간만 어두운 톤(#222)으로, 양 끝 외곽은 밝은 회색(#ddd) 처리
            sliderTrack.style.background = `linear-gradient(to right, #ddd ${minPercent}%, #222 ${minPercent}%, #222 ${maxPercent}%, #ddd ${maxPercent}%)`;

            // 텍스트 디스플레이 갱신
            rangeDisplay.textContent = `${minVal}년 ~ ${maxVal}년`;
        }

        // 슬라이더 조작 시 궤적과 검색 실시간 동기화 및 개별 충돌/z-index 방지
        sliderMin.addEventListener("input", () => {
            const minVal = parseInt(sliderMin.value);
            const maxVal = parseInt(sliderMax.value);

            // 현재 조작 중인 최소 슬라이더를 z-index 최상위로 올림
            sliderMin.style.zIndex = "3";
            sliderMax.style.zIndex = "2";

            // 최소 조절점이 최대 조절점을 추월하지 않도록 제어
            if (minVal > maxVal) {
                sliderMin.value = maxVal;
            }

            updateSliderTrack();
            executeSearch();
        });

        sliderMax.addEventListener("input", () => {
            const minVal = parseInt(sliderMin.value);
            const maxVal = parseInt(sliderMax.value);

            // 현재 조작 중인 최대 슬라이더를 z-index 최상위로 올림
            sliderMax.style.zIndex = "3";
            sliderMin.style.zIndex = "2";

            // 최대 조절점이 최소 조절점을 역추월하지 않도록 제어
            if (maxVal < minVal) {
                sliderMax.value = minVal;
            }

            updateSliderTrack();
            executeSearch();
        });

        // 초기 궤적 컬러 정돈
        updateSliderTrack();

        // 간단한 토크나이저 (조사 제거 보정)
        function tokenize(text) {
            if (!text) return [];
            const rawTokens = text.toLowerCase()
                .replace(/[^a-zA-Z0-9가-힣\\s]/g, "")
                .split(/\\s+/);
            
            return rawTokens.map(token => {
                if (token.length > 2) {
                    return token.replace(/(은|는|이|가|을|를|에|의|로|와|과|하다)$/, "");
                }
                return token;
            }).filter(t => t.length > 0);
        }

        // 단어 빈도수 구하기
        function getTermFrequency(tokens) {
            const tf = {};
            tokens.forEach(token => {
                tf[token] = (tf[token] || 0) + 1;
            });
            return tf;
        }

        // 코사인 유사도 계산
        function calculateCosineSimilarity(queryTokens, docTokens) {
            if (queryTokens.length === 0 || docTokens.length === 0) return 0;

            const queryTf = getTermFrequency(queryTokens);
            const docTf = getTermFrequency(docTokens);

            const allWords = new Set([...Object.keys(queryTf), ...Object.keys(docTf)]);

            let dotProduct = 0;
            let queryMagSq = 0;
            let docMagSq = 0;

            allWords.forEach(word => {
                const qCount = queryTf[word] || 0;
                const dCount = docTf[word] || 0;

                dotProduct += qCount * dCount;
                queryMagSq += qCount * qCount;
                docMagSq += dCount * dCount;
            });

            if (queryMagSq === 0 || docMagSq === 0) return 0;
            return dotProduct / (Math.sqrt(queryMagSq) * Math.sqrt(docMagSq));
        }

        // 스니펫 생성
        function getSnippet(content, queryText) {
            if (!queryText) return content.substring(0, 150) + "...";
            
            const words = queryText.split(/\\s+/).filter(w => w.length > 0);
            let bestIdx = 0;
            let maxMatch = 0;

            for (let i = 0; i < content.length - 120; i += 20) {
                const subText = content.substring(i, i + 150).toLowerCase();
                let matchCount = 0;
                words.forEach(word => {
                    if (subText.includes(word.toLowerCase())) {
                        matchCount++;
                    }
                });
                if (matchCount > maxMatch) {
                    maxMatch = matchCount;
                    bestIdx = i;
                }
            }
            
            const start = Math.max(0, bestIdx - 30);
            const end = Math.min(content.length, start + 160);
            let snippet = (start > 0 ? "..." : "") + content.substring(start, end);
            if (end < content.length) snippet += "...";
            
            words.forEach(word => {
                const regex = new RegExp(`(${word})`, 'gi');
                snippet = snippet.replace(regex, `<mark style="background-color: #ffeb3b; padding: 1px 3px; border-radius: 2px; color: #000;">$1</mark>`);
            });
            return snippet;
        }

        // 검색 실행 및 필터 연동
        function executeSearch() {
            const queryText = searchInput.value.trim();
            const queryTokens = tokenize(queryText);

            const selectedCategories = Array.from(document.querySelectorAll(".filter-category:checked"))
                .map(cb => cb.value);

            const minYear = parseInt(sliderMin.value);
            const maxYear = parseInt(sliderMax.value);

            let results = [];

            if (queryText === "") {
                results = SEARCH_DATA.filter(doc => {
                    const docYear = parseInt(doc.date.substring(0, 4));
                    return selectedCategories.includes(doc.category) && 
                           docYear >= minYear && 
                           docYear <= maxYear;
                }).map(doc => ({
                    doc: doc,
                    similarity: 0
                })).sort((a, b) => new Date(b.doc.date) - new Date(a.doc.date));
            } else {
                SEARCH_DATA.forEach(doc => {
                    const docYear = parseInt(doc.date.substring(0, 4));
                    if (selectedCategories.includes(doc.category) && 
                        docYear >= minYear && 
                        docYear <= maxYear) {
                        
                        const docTokens = tokenize(doc.title + " " + doc.content);
                        const sim = calculateCosineSimilarity(queryTokens, docTokens);
                        
                        let bonus = 0;
                        queryTokens.forEach(token => {
                            if (doc.title.toLowerCase().includes(token.toLowerCase())) bonus += 0.15;
                        });

                        const finalSim = Math.min(1.0, sim + bonus);

                        if (finalSim > 0.01) {
                            results.push({
                                doc: doc,
                                similarity: finalSim
                            });
                        }
                    }
                });

                results.sort((a, b) => b.similarity - a.similarity);
            }

            currentFilteredResults = results;
            currentPage = 1; 
            renderResults();
        }

        // 결과 렌더링
        function renderResults() {
            resultsContainer.innerHTML = "";
            paginationWrapper.innerHTML = "";

            const totalResults = currentFilteredResults.length;
            const queryText = searchInput.value.trim();

            if (queryText === "") {
                metaBar.textContent = `전체 목록 탐색 모드 (필터 부합 글: 총 ${totalResults}개)`;
            } else {
                metaBar.textContent = `"${queryText}" 검색 결과: 유사 연관 글 ${totalResults}개 매치 완료`;
            }

            if (totalResults === 0) {
                resultsContainer.innerHTML = `
                    <div style="text-align: center; padding: 40px 0; color: #888; border: 1px dashed #ccc; background-color: #fafafa; font-family: monospace;">
                        지정된 기간(${sliderMin.value}년~${sliderMax.value}년) 및 조건에 일치하는 결과가 없습니다.<br>필터를 넓히거나 다른 키워드를 입력해 보세요.
                    </div>
                `;
                return;
            }

            const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
            const endIndex = Math.min(startIndex + ITEMS_PER_PAGE, totalResults);
            const pageItems = currentFilteredResults.slice(startIndex, endIndex);

            const listEl = document.createElement("div");
            pageItems.forEach(item => {
                const card = document.createElement("div");
                card.className = "search-result-card";

                const meta = document.createElement("div");
                meta.className = "search-result-meta";
                
                const simPercent = Math.round(item.similarity * 100);
                const similarityBadge = item.similarity > 0 
                    ? `<span class="search-result-similarity">정확도 ${simPercent}%</span>` 
                    : '';

                meta.innerHTML = `
                    <span>📁 ${item.doc.category}</span>
                    <span>📅 ${item.doc.date}</span>
                    ${similarityBadge}
                `;

                const title = document.createElement("h2");
                title.className = "search-result-title";
                title.innerHTML = `<a href="${item.doc.url}">${item.doc.title}</a>`;

                const snippet = document.createElement("p");
                snippet.className = "search-result-snippet";
                snippet.innerHTML = getSnippet(item.doc.content, queryText);

                card.appendChild(meta);
                card.appendChild(title);
                card.appendChild(snippet);
                listEl.appendChild(card);
            });
            resultsContainer.appendChild(listEl);

            const totalPages = Math.ceil(totalResults / ITEMS_PER_PAGE);
            if (totalPages > 1) {
                const prevBtn = document.createElement("button");
                prevBtn.className = `pagination-btn ${currentPage === 1 ? 'disabled' : ''}`;
                prevBtn.textContent = "< 이전";
                prevBtn.disabled = (currentPage === 1);
                prevBtn.addEventListener("click", () => {
                    if (currentPage > 1) {
                        currentPage--;
                        renderResults();
                        window.scrollTo(0, 0);
                    }
                });
                paginationWrapper.appendChild(prevBtn);

                for (let i = 1; i <= totalPages; i++) {
                    const pageBtn = document.createElement("button");
                    pageBtn.className = `pagination-btn ${currentPage === i ? 'active' : ''}`;
                    pageBtn.textContent = i;
                    pageBtn.addEventListener("click", () => {
                        if (currentPage !== i) {
                            currentPage = i;
                            renderResults();
                            window.scrollTo(0, 0);
                        }
                    });
                    paginationWrapper.appendChild(pageBtn);
                }

                const nextBtn = document.createElement("button");
                nextBtn.className = `pagination-btn ${currentPage === totalPages ? 'disabled' : ''}`;
                nextBtn.textContent = "다음 >";
                nextBtn.disabled = (currentPage === totalPages);
                nextBtn.addEventListener("click", () => {
                    if (currentPage < totalPages) {
                        currentPage++;
                        renderResults();
                        window.scrollTo(0, 0);
                    }
                });
                paginationWrapper.appendChild(nextBtn);
            }
        }

        searchBtn.addEventListener("click", executeSearch);
        searchInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                executeSearch();
            }
        });

        document.querySelectorAll(".filter-category").forEach(cb => {
            cb.addEventListener("change", executeSearch);
        });

        executeSearch();
    });
</script>
"""

# 매우 가벼운 정규식 기반 마크다운 -> HTML 파서
def parse_markdown_to_html(md_text):
    lines = md_text.split('\n')
    html_lines = []
    in_list = False
    in_quote = False

    for line in lines:
        stripped = line.strip()

        if in_list and not (stripped.startswith('- ') or stripped.startswith('* ')):
            html_lines.append("</ul>")
            in_list = False

        if in_quote and not stripped.startswith('> '):
            html_lines.append("</blockquote>")
            in_quote = False

        if not stripped:
            continue

        if stripped.startswith('### '):
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith('## '):
            html_lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith('# '):
            html_lines.append(f"<h1>{stripped[2:]}</h1>")

        elif stripped.startswith('> '):
            content = stripped[2:]
            if not in_quote:
                html_lines.append("<blockquote>")
                in_quote = True
            html_lines.append(f"<p>{content}</p>")

        elif stripped.startswith('- ') or stripped.startswith('* '):
            content = stripped[2:]
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
            html_lines.append(f"<li>{content}</li>")

        else:
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', stripped)
            content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="text-decoration:underline; color:#0000ee;">\1</a>', content)
            html_lines.append(f"<p>{content}</p>")

    if in_list:
        html_lines.append("</ul>")
    if in_quote:
        html_lines.append("</blockquote>")

    return '\n'.join(html_lines)


def build_site():
    print("통합 정적 웹 빌더 구동 중...")
    
    posts_dir = "_posts"
    if not os.path.exists(posts_dir):
        os.makedirs(posts_dir)

    all_posts = []

    # _posts 디렉토리 내 md 파일 스캔
    for filename in os.listdir(posts_dir):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(posts_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw_content, re.DOTALL)
        if not frontmatter_match:
            print(f"[Warning] {filename} 은 YAML 설정 규격(---)에 맞지 않아 빌드에서 생략합니다.")
            continue

        metadata_raw = frontmatter_match.group(1)
        markdown_body = frontmatter_match.group(2).strip()

        metadata = {}
        for line in metadata_raw.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                metadata[key.strip()] = val.strip()

        title = metadata.get("title", "무제")
        category = metadata.get("category", "일기장")
        date_str = metadata.get("date", datetime.today().strftime('%Y-%m-%d'))

        if category not in CATEGORY_MAP:
            category = "일기장"

        html_filename = filename.replace('.md', '.html')
        target_folder = CATEGORY_MAP[category]
        target_path = os.path.join(target_folder, html_filename)

        html_content = parse_markdown_to_html(markdown_body)
        
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            date_formatted = dt.strftime("%Y년 %m월 %d일")
        except ValueError:
            date_formatted = date_str

        plain_text = re.sub(r'<[^>]*>', '', html_content)
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        description = plain_text[:120] + "..." if len(plain_text) > 120 else plain_text

        # 포스트 데이터 누적
        post_data = {
            "title": title,
            "category": category,
            "date": date_str,
            "filename": html_filename,
            "url": f"{target_folder}/{html_filename}",
            "content": plain_text,
            "description": description
        }
        all_posts.append(post_data)

        # 개별 HTML 포스트 파일 생성 (depth=1 상대경로)
        article_content = f"""<header>
    <h1>{title}</h1>
    <div class="date">작성일: {date_formatted}</div>
</header>
<article>
    {html_content}
    <p style="margin-top: 40px;">
        <a id="back-to-list" href="index.html" style="text-decoration: underline; color: #0000ee;">← 목록으로 돌아가기</a>
    </p>
</article>"""

        post_html = render_html_layout(
            title=title,
            content=article_content,
            depth=1,
            description=description
        )
        
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(post_html)
        print(f"[Post Built] {target_path} 작성 완료")

    # -----------------------------------------------------------------
    # 각 카테고리별 index.html (목록 페이지) 동적 갱신
    # -----------------------------------------------------------------
    category_descriptions = {
        "일기장": "일상의 소소한 생각과 있었던 일들을 기록하는 공간입니다.",
        "Notes": "학습하고 배운 기술 지식과 개념들을 정돈해 둔 공간입니다.",
        "Projects": "수행한 연구와 개인 프로젝트 성과를 모아둔 기록입니다.",
        "사색 일지": "길을 걷거나 차를 마시며 문득 스쳐 갔던 깊은 사유들의 조각입니다."
    }

    for cat_name, folder_name in CATEGORY_MAP.items():
        cat_posts = [p for p in all_posts if p["category"] == cat_name]
        cat_posts.sort(key=lambda x: x["date"], reverse=True)

        table_rows = []
        if not cat_posts:
            table_rows.append(
                f'<tr style="border-bottom: 1px solid #ddd;">'
                f'<td style="padding: 10px 0; color: #888; font-style: italic;" colspan="2">'
                f'아직 등록된 기록물이 없습니다. _posts 폴더에 새 글을 올려보세요.'
                f'</td></tr>'
            )
        else:
            for p in cat_posts:
                table_rows.append(
                    f'<tr style="border-bottom: 1px solid #ddd;">\n'
                    f'    <td style="padding: 10px 0; color: #666;">{p["date"]}</td>\n'
                    f'    <td style="padding: 10px 0;">\n'
                    f'        <a href="{p["filename"]}" style="text-decoration: underline; color: #0000ee;">{p["title"]}</a>\n'
                    f'    </td>\n'
                    f'</tr>'
                )

        index_content = f"""<header>
    <h1>{cat_name}</h1>
    <p>{category_descriptions[cat_name]}</p>
    <div class="date">기록된 게시물 개수: {len(cat_posts)}개</div>
</header>
<article>
    <h2>글 목록</h2>
    <table style="width: 100%; border-collapse: collapse; margin-top: 20px; font-family: monospace;">
        <thead>
            <tr style="border-bottom: 2px solid #333; text-align: left;">
                <th style="padding: 8px 0; width: 120px;">날짜</th>
                <th style="padding: 8px 0;">제목</th>
            </tr>
        </thead>
        <tbody>
            {"".join(table_rows)}
        </tbody>
    </table>
</article>"""

        index_html = render_html_layout(
            title=cat_name,
            content=index_content,
            depth=1,
            description=f"{cat_name} 기록을 정돈해 둔 목록 페이지"
        )

        index_path = os.path.join(folder_name, "index.html")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_html)
        print(f"[Index Updated] {index_path} 목록 동기화 완료")

    # -----------------------------------------------------------------
    # 통합 검색용 search_data.json 구성
    # -----------------------------------------------------------------
    search_data_list = [
        {
            "url": "index.html",
            "title": "Art of Life - 홈 소개",
            "category": "소개",
            "date": "2026-07-09",
            "content": "환영합니다 이곳은 저의 소소한 일상 관심사 흘러가는 생각들을 차분히 적어두는 개인 홈페이지입니다 화려한 장식이나 복잡한 기능 없이 오직 텍스트와 단순한 구조로만 구성된 클래식한 공간입니다 지나치게 빠르고 시끄러운 인터넷 세상 속에서 잠시 쉬어가는 마음으로 글을 쓰고 정리하고 있습니다 일상 일기 하루 동안 겪었던 소소한 이야기나 감정들 관심사 독서 음악 프로그래밍 등 요즘 깊게 들여다보고 있는 것들에 대한 생각 단상 길을 걷다 문득 든 생각이나 짧은 메모들 단순함은 궁극의 정교함이다 레오나르도 다빈치"
        },
        {
            "url": "about.html",
            "title": "자기소개 (About Me)",
            "category": "소개",
            "date": "2026-07-11",
            "content": "안녕하세요 이곳은 저의 소소한 생각들과 하루하루의 일상 그리고 깊어가는 관심사들을 모아두는 정적 웹사이트입니다 화려한 장식 없이 단순한 텍스트로 가득 찬 이 공간처럼 저 역시 본질적이고 명료한 것을 좋아합니다 역할 소프트웨어 엔지니어 테크니컬 라이터 관심사 웹 표준 정적 사이트 아키텍처 정보 설계 미니멀리즘 좋아하는 것 차분한 음악 듣기 책 읽기 사소한 일상의 기록 조용한 산책 가치관 덜어내는 삶 꾸준한 아카이빙 자신만의 속도 커리어 기술 개인 프로젝트 프리랜서 클라우드 솔루션사 주니어 개발자 프론트엔드 백엔드 유지보수 웹 접근성 개선 Git 마크다운 리눅스 Vim 에디터 연혁 2026년 7월 홈페이지 개설 2024년 3월 정적 웹 기술과 미니멀 인터페이스 디자인 공부 2021년 1월 프로그래밍 입문 2018년 9월 글쓰기 습관 장비 하드웨어 맥북 에어 맥북에어 HHKB 키보드 해피해킹 프로페셔널 클래식 몰스킨 플레인 노트 소프트웨어 비주얼 스튜디오 코드 VS Code Vim 옴니아웃라이너 Obsidian 옵시디언 파이어폭스 개발자 에디션 드립 커피 예가체프 아이스 우롱차"
        }
    ]

    for p in all_posts:
        search_data_list.append({
            "url": p["url"],
            "title": p["title"],
            "category": p["category"],
            "date": p["date"],
            "content": p["content"]
        })

    json_data = json.dumps(search_data_list, ensure_ascii=False, indent=4)
    with open("search_data.json", 'w', encoding='utf-8') as f:
        f.write(json_data)
    print("[Sync] search_data.json 갱신 완료")

    # -----------------------------------------------------------------
    # 루트 정적 파일 3개 컴파일 (index.html, about.html, search.html)
    # -----------------------------------------------------------------
    # 1. index.html 생성 (depth=0)
    index_html = render_html_layout(
        title="홈",
        content=INDEX_BODY,
        depth=0,
        description="일상의 일기와 관심사, 생각을 기록하는 클래식한 개인 홈페이지"
    )
    with open("index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("[Core Built] index.html 갱신 완료")

    # 2. about.html 생성 (depth=0)
    about_html = render_html_layout(
        title="소개",
        content=ABOUT_BODY,
        depth=0,
        description="가치관, 커리어, 연혁, 사용하는 장비를 한눈에 보여주는 종합 자기소개 페이지"
    )
    with open("about.html", 'w', encoding='utf-8') as f:
        f.write(about_html)
    print("[Core Built] about.html 갱신 완료")

    # 3. search.html 생성 (depth=0, SEARCH_DATA 치환 포함)
    search_html_raw = render_html_layout(
        title="검색",
        content=SEARCH_BODY,
        depth=0,
        description="코사인 유사도 분석 기반의 정밀 본문 검색 및 카테고리/기간별 필터 제공"
    )
    pattern = r'(/\*DATA_START\*/)(.*?)(/\*DATA_END\*/)'
    search_html_compiled = re.sub(pattern, lambda m: m.group(1) + json_data + m.group(3), search_html_raw, flags=re.DOTALL)
    
    with open("search.html", 'w', encoding='utf-8') as f:
        f.write(search_html_compiled)
    print("[Core Built] search.html 갱신 완료")

    # -----------------------------------------------------------------
    # 구글 검색 최적화용 sitemap.xml 및 robots.txt 생성 자동화
    # -----------------------------------------------------------------
    # 1. sitemap.xml 빌드
    today_str = datetime.today().strftime('%Y-%m-%d')
    sitemap_urls = [
        f"    <url>\n        <loc>{SITE_DOMAIN}/index.html</loc>\n        <lastmod>{today_str}</lastmod>\n        <priority>1.0</priority>\n    </url>",
        f"    <url>\n        <loc>{SITE_DOMAIN}/about.html</loc>\n        <lastmod>{today_str}</lastmod>\n        <priority>0.8</priority>\n    </url>",
        f"    <url>\n        <loc>{SITE_DOMAIN}/search.html</loc>\n        <lastmod>{today_str}</lastmod>\n        <priority>0.8</priority>\n    </url>"
    ]
    
    for cat_name, folder_name in CATEGORY_MAP.items():
        sitemap_urls.append(
            f"    <url>\n        <loc>{SITE_DOMAIN}/{folder_name}/index.html</loc>\n        <lastmod>{today_str}</lastmod>\n        <priority>0.7</priority>\n    </url>"
        )

    for p in all_posts:
        sitemap_urls.append(
            f"    <url>\n        <loc>{SITE_DOMAIN}/{p['url']}</loc>\n        <lastmod>{p['date']}</lastmod>\n        <priority>0.6</priority>\n    </url>"
        )

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(sitemap_urls)}
</urlset>
"""
    with open("sitemap.xml", 'w', encoding='utf-8') as f:
        f.write(sitemap_xml)
    print("[SEO Built] sitemap.xml 자동 제너레이션 완료")

    # 2. robots.txt 빌드
    robots_txt = f"""User-agent: *
Allow: /

Sitemap: {SITE_DOMAIN}/sitemap.xml
"""
    with open("robots.txt", 'w', encoding='utf-8') as f:
        f.write(robots_txt)
    print("[SEO Built] robots.txt 자동 제너레이션 완료")

    print("통합 정적 컴파일 및 배포 최적화 빌드가 대성공적으로 완료되었습니다!")


if __name__ == "__main__":
    build_site()
