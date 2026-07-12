// theme.js - 테마 관리, 모바일 토글 및 자동 목차(TOC) 생성 스크립트

// 1. 페이지 로딩 즉시 테마 적용 (깜빡임 최소화)
(function() {
    const savedTheme = localStorage.getItem('site-theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        document.body?.classList.add('dark-mode');
    } else if (savedTheme === 'sepia') {
        document.documentElement.classList.add('sepia-mode');
        document.body?.classList.add('sepia-mode');
    }
})();

// 전역 테마 갱신 함수
window.setTheme = function(themeName) {
    // 기존 클래스 제거
    document.documentElement.classList.remove('dark-mode', 'sepia-mode');
    document.body.classList.remove('dark-mode', 'sepia-mode');

    // 새 테마 추가 및 저장
    if (themeName === 'dark') {
        document.documentElement.classList.add('dark-mode');
        document.body.classList.add('dark-mode');
    } else if (themeName === 'sepia') {
        document.documentElement.classList.add('sepia-mode');
        document.body.classList.add('sepia-mode');
    }
    
    localStorage.setItem('site-theme', themeName);
    updateActiveThemeLink(themeName);
};

// 테마 선택 링크 활성화 시각적 갱신
function updateActiveThemeLink(themeName) {
    document.querySelectorAll('.theme-link').forEach(link => {
        link.style.fontWeight = 'normal';
        link.style.textDecoration = 'underline';
    });
    const activeLink = document.getElementById(`theme-${themeName}`);
    if (activeLink) {
        activeLink.style.fontWeight = 'bold';
        activeLink.style.textDecoration = 'none';
    }
}

document.addEventListener("DOMContentLoaded", () => {
    // 로딩 완료 후 저장된 테마 한 번 더 체크 (body 로드 보완)
    const currentTheme = localStorage.getItem('site-theme') || 'light';
    window.setTheme(currentTheme);

    // 2. 모바일 네비게이션 메뉴 접기/펼치기 토글
    const sidebar = document.querySelector(".sidebar");
    const toggleBtn = document.getElementById("menu-toggle");
    
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("menu-open");
            // 펼쳐진 상태에 따라 버튼 텍스트 변경
            if (sidebar.classList.contains("menu-open")) {
                toggleBtn.textContent = "Close ✕";
            } else {
                toggleBtn.textContent = "Menu ☰";
            }
        });
    }

    // 3. 본문 H2 제목 스캔 및 목차(TOC) 자동 조립
    const article = document.querySelector("main.content article");
    if (article) {
        const h2Elements = article.querySelectorAll("h2");
        
        // H2가 2개 이상일 때만 목차 박스 자동 생성
        if (h2Elements.length >= 2) {
            const tocBox = document.createElement("div");
            tocBox.className = "toc-box";
            
            const tocTitle = document.createElement("div");
            tocTitle.className = "toc-title";
            tocTitle.textContent = "목차 (Table of Contents)";
            tocBox.appendChild(tocTitle);

            const tocList = document.createElement("ul");
            
            h2Elements.forEach((h2, index) => {
                // H2에 고유 고정 ID 부여
                const tocId = `toc-section-${index}`;
                h2.id = tocId;

                // 목차 링크 조립
                const listItem = document.createElement("li");
                const link = document.createElement("a");
                link.href = `#${tocId}`;
                link.textContent = h2.textContent;
                
                // 클릭 시 부드러운 스크롤 이동
                link.addEventListener("click", (e) => {
                    e.preventDefault();
                    h2.scrollIntoView({ behavior: "smooth", block: "start" });
                    history.pushState(null, null, `#${tocId}`); // URL 해시 업데이트
                });

                listItem.appendChild(link);
                tocList.appendChild(listItem);
            });

            tocBox.appendChild(tocList);

            // 본문 기사(article) 맨 위에 목차 삽입 (프로필 이미지 figure가 있다면 그 뒤 혹은 글 최상단에 배치)
            const firstChild = article.firstChild;
            if (firstChild) {
                article.insertBefore(tocBox, firstChild);
            } else {
                article.appendChild(tocBox);
            }
        }
    }
});
