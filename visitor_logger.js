// 방문자 로그 시스템
class VisitorLogger {
    constructor() {
        this.logData = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            referrer: document.referrer,
            userAgent: navigator.userAgent,
            screenResolution: `${screen.width}x${screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            language: navigator.language
        };
        
        this.logVisit();
    }
    
    logVisit() {
        // localStorage에 방문 로그 저장
        const logs = JSON.parse(localStorage.getItem('visitorLogs') || '[]');
        
        // 중복 방문 체크 (같은 세션에서는 로그하지 않음)
        const sessionId = this.getSessionId();
        const existingLog = logs.find(log => log.sessionId === sessionId && log.url === this.logData.url);
        
        if (!existingLog) {
            const logEntry = {
                ...this.logData,
                sessionId: sessionId,
                visitId: this.generateVisitId()
            };
            
            logs.push(logEntry);
            
            // 최대 100개의 로그만 유지
            if (logs.length > 100) {
                logs.splice(0, logs.length - 100);
            }
            
            localStorage.setItem('visitorLogs', JSON.stringify(logs));
            
            console.log('📊 Visit logged:', logEntry);
            this.updateStats();
        }
    }
    
    getSessionId() {
        let sessionId = sessionStorage.getItem('sessionId');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('sessionId', sessionId);
        }
        return sessionId;
    }
    
    generateVisitId() {
        return 'visit_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    updateStats() {
        const logs = JSON.parse(localStorage.getItem('visitorLogs') || '[]');
        
        // 통계 계산
        const stats = {
            totalVisits: logs.length,
            uniquePages: [...new Set(logs.map(log => log.url))].length,
            todayVisits: logs.filter(log => {
                const today = new Date().toDateString();
                const logDate = new Date(log.timestamp).toDateString();
                return today === logDate;
            }).length,
            lastVisit: logs[logs.length - 1]?.timestamp
        };
        
        // 통계를 화면에 표시 (선택사항)
        this.displayStats(stats);
        
        // 통계를 localStorage에 저장
        localStorage.setItem('visitorStats', JSON.stringify(stats));
    }
    
    displayStats(stats) {
        // 페이지 하단에 통계 표시 (개발자용)
        const statsDiv = document.createElement('div');
        statsDiv.style.cssText = `
            position: fixed;
            bottom: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            z-index: 9999;
            font-family: monospace;
        `;
        
        statsDiv.innerHTML = `
            📊 Stats: ${stats.totalVisits} visits | ${stats.uniquePages} pages | ${stats.todayVisits} today
        `;
        
        // 개발자 모드일 때만 표시
        if (window.location.hostname === 'localhost' || window.location.hostname.includes('127.0.0.1')) {
            document.body.appendChild(statsDiv);
        }
    }
    
    // 방문 로그 내보내기 (개발자용)
    exportLogs() {
        const logs = JSON.parse(localStorage.getItem('visitorLogs') || '[]');
        const stats = JSON.parse(localStorage.getItem('visitorStats') || '{}');
        
        const exportData = {
            exportedAt: new Date().toISOString(),
            stats: stats,
            logs: logs
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `visitor-logs-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }
}

// 페이지 로드 시 방문자 로거 초기화
document.addEventListener('DOMContentLoaded', function() {
    new VisitorLogger();
});

// 개발자 콘솔에서 로그 내보내기
window.exportVisitorLogs = function() {
    new VisitorLogger().exportLogs();
};

console.log('📊 Visitor Logger initialized. Use exportVisitorLogs() to download logs.');
