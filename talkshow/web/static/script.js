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
        
        // 计算需要的高度：时间标记数量 * 每格高度
        const timelineHeight = Math.max(600, timeMarkers.length * 50 + 100);
        
        return `
            <div class="timeline-container">
                <div class="timeline-header">
                    <h3>📊 时间轴视图 (半小时刻度)</h3>
                    <span class="text-muted">显示 ${filteredSessions.length} 个会话，${timeMarkers.length} 个时间点</span>
                </div>
                <div class="timeline-view" style="height: ${timelineHeight}px;">
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
                    <div class="time-marker ${marker.isHour ? 'hour-mark' : 'half-hour-mark'} ${marker.isNewDay ? 'new-day' : ''}" data-time="${marker.time}">
                        ${marker.showDate ? `<div class="date-header">${marker.date}</div>` : ''}
                        <div class="time-text ${marker.isHour ? 'hour-text' : 'half-hour-text'}">
                            ${marker.timeDisplay}
                        </div>
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
                    <a href="/view/${encodeURIComponent(session.filename)}" class="session-title text-truncate" title="点击查看原文: ${session.theme}">
                        📄 ${session.theme}
                    </a>
                    <div class="session-meta">
                        <div>${session.qa_count} Q&As</div>
                        <div class="text-small">${this.formatDate(session.created_time)}</div>
                    </div>
                </div>
                <div class="session-content" id="session-${session.filename}">
                    <div class="loading">将显示Q&A摘要...</div>
                </div>
            </div>
        `;
    }
    
    // 计算Q/A在时间轴上的位置
    calculateQAPosition(qaTimestamp, startTime) {
        if (!qaTimestamp || !startTime) return 0;
        
        const qa = new Date(qaTimestamp);
        const start = new Date(startTime);
        
        const minutesDiff = (qa - start) / (1000 * 60); // 分钟差
        const slotHeight = 50; // 每个30分钟格子的高度(px)
        
        return Math.max(0, (minutesDiff / 30) * slotHeight); // 计算top位置
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
                // 获取时间轴的起始时间
                const filteredSessions = this.getFilteredSessions();
                const allTimes = filteredSessions
                    .map(s => s.created_time)
                    .filter(Boolean)
                    .sort();
                
                const startTime = allTimes.length > 0 ? allTimes[0] : null;
                
                container.innerHTML = session.qa_pairs.map((qa, index) => {
                    const position = qa.timestamp ? this.calculateQAPosition(qa.timestamp, startTime) : index * 60;
                    
                    return `
                        <div class="qa-pair" data-qa-index="${index}" style="top: ${position}px;">
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
                    `;
                }).join('');
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
        console.log('设置混合加载策略：立即加载前8个，其余懒加载');
        
        const allSessions = document.querySelectorAll('.session-column');
        console.log(`找到 ${allSessions.length} 个会话列`);
        
        // 立即加载前8个会话的内容，确保用户看到Q&A摘要
        allSessions.forEach((column, index) => {
            const filename = column.dataset.filename;
            if (filename && index < 8) {
                console.log(`立即加载会话 ${index + 1}: ${filename}`);
                this.loadSessionContent(filename);
                column.dataset.loaded = 'true';
            }
        });
        
        // 为剩余的会话设置懒加载
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const filename = entry.target.dataset.filename;
                    if (filename && !entry.target.dataset.loaded) {
                        console.log(`懒加载会话内容: ${filename}`);
                        this.loadSessionContent(filename);
                        entry.target.dataset.loaded = 'true';
                        observer.unobserve(entry.target);
                    }
                }
            });
        }, { threshold: 0.1 });
        
        // 只对第8个之后的会话使用懒加载观察
        allSessions.forEach((column, index) => {
            if (index >= 8) {
                observer.observe(column);
            }
        });
    }
    
    setupScrollSync() {
        const timelineView = document.querySelector('.timeline-view');
        const timeAxis = document.querySelector('.time-axis');
        
        if (timelineView && timeAxis) {
            // 同步垂直滚动
            timelineView.addEventListener('scroll', () => {
                timeAxis.scrollTop = timelineView.scrollTop;
                
                // 高亮当前时间范围
                this.highlightCurrentTimeRange();
            });
            
            // 同步时间轴的滚动
            timeAxis.addEventListener('scroll', () => {
                timelineView.scrollTop = timeAxis.scrollTop;
            });
        }
    }
    
    highlightCurrentTimeRange() {
        const timelineView = document.querySelector('.timeline-view');
        if (!timelineView) return;
        
        const scrollTop = timelineView.scrollTop;
        const viewHeight = timelineView.clientHeight;
        const timeMarkers = document.querySelectorAll('.time-marker');
        
        timeMarkers.forEach((marker, index) => {
            const markerTop = index * 50; // 每个标记50px高度
            const isVisible = markerTop >= scrollTop && markerTop <= scrollTop + viewHeight;
            
            if (isVisible) {
                marker.classList.add('visible');
            } else {
                marker.classList.remove('visible');
            }
        });
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
        
        // Generate time markers every 30 minutes
        const markers = [];
        if (allTimes.length > 0) {
            const start = new Date(allTimes[0]);
            const end = new Date(allTimes[allTimes.length - 1]);
            
            // 从整点或半点开始，对齐到30分钟间隔
            const alignedStart = new Date(start);
            alignedStart.setMinutes(Math.floor(alignedStart.getMinutes() / 30) * 30, 0, 0);
            
            // 确保覆盖到结束时间之后
            const alignedEnd = new Date(end);
            alignedEnd.setMinutes(Math.ceil(alignedEnd.getMinutes() / 30) * 30, 0, 0);
            
            let lastDate = '';
            
            // 每30分钟生成一个时间标记
            for (let time = alignedStart.getTime(); time <= alignedEnd.getTime(); time += 30 * 60 * 1000) {
                const date = new Date(time);
                const currentDate = this.formatDate(date.toISOString());
                const isNewDay = currentDate !== lastDate;
                
                markers.push({
                    time: date.toISOString(),
                    date: currentDate,
                    timeDisplay: this.formatTime(date.toISOString()),
                    isHour: date.getMinutes() === 0, // 标记整点
                    isNewDay: isNewDay, // 标记新的一天
                    showDate: isNewDay && date.getHours() === 0 && date.getMinutes() === 0 // 只在00:00显示日期
                });
                
                if (isNewDay) {
                    lastDate = currentDate;
                }
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

// 清理：移除了弹窗相关代码，现在使用链接跳转