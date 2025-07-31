// TalkShow Frontend JavaScript

class TalkShowApp {
    constructor() {
        this.sessions = [];
        this.stats = {};
        this.timeline = [];
        this.selectedSession = null;
        this.currentTimeFilter = 'all';
        this.searchQuery = '';
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadData();
            this.renderApp();
            this.setupEventListeners();
        } catch (error) {
            this.showError('Failed to initialize app: ' + error.message);
        }
    }
    
    async loadData() {
        try {
            // Load sessions, stats, and timeline in parallel
            const [sessionsResponse, statsResponse, timelineResponse] = await Promise.all([
                fetch('/api/sessions'),
                fetch('/api/stats'),
                fetch('/api/timeline')
            ]);
            
            if (!sessionsResponse.ok || !statsResponse.ok || !timelineResponse.ok) {
                throw new Error('Failed to fetch data from API');
            }
            
            this.sessions = await sessionsResponse.json();
            this.stats = await statsResponse.json();
            this.timeline = await timelineResponse.json();
            
            console.log('Loaded data:', {
                sessions: this.sessions.length,
                timeline: this.timeline.length,
                stats: this.stats
            });
            
        } catch (error) {
            console.error('Error loading data:', error);
            throw error;
        }
    }
    
    renderApp() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="container">
                ${this.renderHeader()}
                ${this.renderStats()}
                ${this.renderControls()}
                ${this.renderTimeline()}
            </div>
        `;
    }
    
    renderHeader() {
        return `
            <div class="header">
                <h1>🎭 TalkShow</h1>
                <p>Chat History Analysis and Visualization</p>
            </div>
        `;
    }
    
    renderStats() {
        return `
            <div class="stats-panel">
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">${this.stats.total_sessions || 0}</div>
                        <div class="stat-label">总会话数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.stats.total_qa_pairs || 0}</div>
                        <div class="stat-label">Q&A对话</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.stats.question_summaries || 0}</div>
                        <div class="stat-label">问题摘要</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.stats.answer_summaries || 0}</div>
                        <div class="stat-label">答案摘要</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.stats.average_qa_per_session || 0}</div>
                        <div class="stat-label">平均Q&A/会话</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.formatFileSize(this.stats.storage_file_size || 0)}</div>
                        <div class="stat-label">数据文件大小</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderControls() {
        const timeOptions = this.getTimeFilterOptions();
        
        return `
            <div class="controls">
                <div class="control-group">
                    <label for="timeFilter">时间筛选:</label>
                    <select id="timeFilter">
                        <option value="all">全部时间</option>
                        ${timeOptions.map(opt => `<option value="${opt.value}">${opt.label}</option>`).join('')}
                    </select>
                </div>
                <div class="control-group">
                    <label for="searchInput">搜索:</label>
                    <input type="text" id="searchInput" placeholder="搜索会话主题或内容...">
                </div>
                <div class="control-group">
                    <button onclick="app.refreshData()">刷新数据</button>
                    <button onclick="app.exportData()">导出数据</button>
                </div>
            </div>
        `;
    }
    
    renderTimeline() {
        const filteredSessions = this.getFilteredSessions();
        const timeMarkers = this.generateTimeMarkers(filteredSessions);
        
        return `
            <div class="timeline-container">
                <div class="timeline-header">
                    <h3>📊 时间轴视图</h3>
                    <span class="text-muted">显示 ${filteredSessions.length} 个会话</span>
                </div>
                <div class="timeline-view">
                    ${this.renderTimeAxis(timeMarkers)}
                    ${this.renderSessionsGrid(filteredSessions)}
                </div>
            </div>
        `;
    }
    
    renderTimeAxis(timeMarkers) {
        return `
            <div class="time-axis">
                ${timeMarkers.map(marker => `
                    <div class="time-marker" data-time="${marker.time}">
                        <div style="font-weight: bold;">${marker.date}</div>
                        <div class="text-small text-muted">${marker.time}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    renderSessionsGrid(sessions) {
        return `
            <div class="sessions-grid">
                ${sessions.map(session => this.renderSessionColumn(session)).join('')}
            </div>
        `;
    }
    
    renderSessionColumn(session) {
        return `
            <div class="session-column" data-filename="${session.filename}">
                <div class="session-header">
                    <div class="session-title text-truncate" title="${session.theme}">
                        ${session.theme}
                    </div>
                    <div class="session-meta">
                        <div>${session.qa_count} Q&As</div>
                        <div class="text-small">${this.formatDate(session.created_time)}</div>
                    </div>
                </div>
                <div class="session-content" id="session-${session.filename}">
                    <div class="loading">加载中...</div>
                </div>
            </div>
        `;
    }
    
    async loadSessionContent(filename) {
        try {
            const response = await fetch(`/api/sessions/${encodeURIComponent(filename)}`);
            if (!response.ok) {
                throw new Error('Failed to load session content');
            }
            
            const session = await response.json();
            const container = document.getElementById(`session-${filename}`);
            
            if (container) {
                container.innerHTML = session.qa_pairs.map((qa, index) => `
                    <div class="qa-pair" data-qa-index="${index}">
                        <div class="question">
                            <div class="question-text">
                                ${qa.question_summary || this.truncateText(qa.question, 100)}
                            </div>
                        </div>
                        <div class="answer">
                            <div class="answer-text">
                                ${qa.answer_summary || this.truncateText(qa.answer, 150)}
                            </div>
                        </div>
                        ${qa.timestamp ? `<div class="qa-timestamp">${this.formatDateTime(qa.timestamp)}</div>` : ''}
                    </div>
                `).join('');
            }
            
        } catch (error) {
            console.error('Error loading session content:', error);
            const container = document.getElementById(`session-${filename}`);
            if (container) {
                container.innerHTML = '<div class="error">加载失败</div>';
            }
        }
    }
    
    setupEventListeners() {
        // Time filter
        const timeFilter = document.getElementById('timeFilter');
        if (timeFilter) {
            timeFilter.addEventListener('change', (e) => {
                this.currentTimeFilter = e.target.value;
                this.updateTimeline();
            });
        }
        
        // Search input
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase();
                this.updateTimeline();
            });
        }
        
        // Load session content when columns become visible
        this.setupIntersectionObserver();
        
        // Setup scroll synchronization
        this.setupScrollSync();
    }
    
    setupIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const filename = entry.target.dataset.filename;
                    if (filename) {
                        this.loadSessionContent(filename);
                        observer.unobserve(entry.target);
                    }
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('.session-column').forEach(column => {
            observer.observe(column);
        });
    }
    
    setupScrollSync() {
        const timelineView = document.querySelector('.timeline-view');
        const timeAxis = document.querySelector('.time-axis');
        
        if (timelineView && timeAxis) {
            timelineView.addEventListener('scroll', () => {
                // You can add scroll synchronization logic here
                // For example, highlighting the current time marker based on scroll position
            });
        }
    }
    
    getFilteredSessions() {
        let filtered = [...this.sessions];
        
        // Apply time filter
        if (this.currentTimeFilter !== 'all') {
            const filterDate = new Date(this.currentTimeFilter);
            filtered = filtered.filter(session => {
                if (!session.created_time) return false;
                const sessionDate = new Date(session.created_time);
                return sessionDate >= filterDate;
            });
        }
        
        // Apply search filter
        if (this.searchQuery) {
            filtered = filtered.filter(session => 
                session.theme.toLowerCase().includes(this.searchQuery) ||
                (session.first_question && session.first_question.toLowerCase().includes(this.searchQuery))
            );
        }
        
        return filtered;
    }
    
    getTimeFilterOptions() {
        if (!this.sessions.length) return [];
        
        const dates = this.sessions
            .map(s => s.created_time)
            .filter(Boolean)
            .sort();
        
        if (!dates.length) return [];
        
        const options = [];
        const now = new Date();
        const oneDay = 24 * 60 * 60 * 1000;
        
        // Last 24 hours
        options.push({
            value: new Date(now - oneDay).toISOString(),
            label: '过去24小时'
        });
        
        // Last week
        options.push({
            value: new Date(now - 7 * oneDay).toISOString(),
            label: '过去一周'
        });
        
        // Last month
        options.push({
            value: new Date(now - 30 * oneDay).toISOString(),
            label: '过去一月'
        });
        
        return options;
    }
    
    generateTimeMarkers(sessions) {
        const allTimes = sessions
            .map(s => s.created_time)
            .filter(Boolean)
            .sort();
        
        // Generate time markers for every few hours/days depending on the span
        const markers = [];
        if (allTimes.length > 0) {
            const start = new Date(allTimes[0]);
            const end = new Date(allTimes[allTimes.length - 1]);
            const span = end - start;
            
            // Create markers based on time span
            const interval = span > 7 * 24 * 60 * 60 * 1000 ? 24 * 60 * 60 * 1000 : 6 * 60 * 60 * 1000; // 1 day or 6 hours
            
            for (let time = start.getTime(); time <= end.getTime(); time += interval) {
                const date = new Date(time);
                markers.push({
                    time: date.toISOString(),
                    date: this.formatDate(date.toISOString()),
                    time: this.formatTime(date.toISOString())
                });
            }
        }
        
        return markers;
    }
    
    updateTimeline() {
        const timelineContainer = document.querySelector('.timeline-container');
        if (timelineContainer) {
            timelineContainer.outerHTML = this.renderTimeline();
            this.setupEventListeners();
        }
    }
    
    async refreshData() {
        try {
            this.showLoading();
            await this.loadData();
            this.renderApp();
            this.setupEventListeners();
        } catch (error) {
            this.showError('刷新数据失败: ' + error.message);
        }
    }
    
    exportData() {
        const data = {
            sessions: this.sessions,
            stats: this.stats,
            timeline: this.timeline,
            exported_at: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `talkshow_export_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    }
    
    // Utility functions
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('zh-CN');
    }
    
    formatTime(dateString) {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    }
    
    formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleString('zh-CN');
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    showLoading() {
        const app = document.getElementById('app');
        app.innerHTML = '<div class="loading">加载中...</div>';
    }
    
    showError(message) {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="container">
                <div class="error">
                    <strong>错误:</strong> ${message}
                </div>
                <button onclick="location.reload()">重新加载</button>
            </div>
        `;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TalkShowApp();
});

// Global functions for button clicks
window.app = null;