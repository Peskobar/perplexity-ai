/**
 * Demokratyzator AI - Main JavaScript
 * Główne funkcje aplikacji
 */

// Globalne zmienne
window.DemokratyzatorAI = {
    version: '1.0.0',
    debug: true,
    apiEndpoints: {
        chat: '/chat/send',
        proxy: 'http://localhost:9000/proxy/chat',
        proxyStatus: '/api/proxy_status',
        models: '/proxy/models'
    },
    currentSession: null,
    settings: {
        autoScroll: true,
        soundNotifications: false,
        darkMode: true
    }
};

// Utility functions
const Utils = {
    /**
     * Formatuje datę do czytelnego formatu
     */
    formatDate(date) {
        return new Intl.DateTimeFormat('pl-PL', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },

    /**
     * Generuje unikalny identyfikator
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },

    /**
     * Pokazuje toast notification
     */
    showToast(message, type = 'info', duration = 5000) {
        const toastContainer = this.getOrCreateToastContainer();
        const toastId = this.generateId();
        
        const toastHtml = `
            <div id="toast-${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i data-feather="${this.getToastIcon(type)}" class="me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(`toast-${toastId}`);
        const toast = new bootstrap.Toast(toastElement, { delay: duration });
        
        // Aktualizuj ikony Feather
        feather.replace();
        
        toast.show();
        
        // Usuń element po ukryciu
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    },

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'alert-circle',
            warning: 'alert-triangle',
            info: 'info'
        };
        return icons[type] || 'info';
    },

    getOrCreateToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        return container;
    },

    /**
     * Kopiuje tekst do schowka
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Skopiowano do schowka', 'success', 2000);
            return true;
        } catch (err) {
            console.error('Błąd kopiowania:', err);
            this.showToast('Błąd kopiowania do schowka', 'error');
            return false;
        }
    },

    /**
     * Pobiera plik
     */
    downloadFile(content, filename, contentType = 'text/plain') {
        const blob = new Blob([content], { type: contentType });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    },

    /**
     * Validuje JSON
     */
    isValidJSON(str) {
        try {
            JSON.parse(str);
            return true;
        } catch (e) {
            return false;
        }
    },

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Formatuje rozmiar pliku
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Sprawdza czy element jest widoczny
     */
    isElementVisible(element) {
        const rect = element.getBoundingClientRect();
        return rect.top >= 0 && rect.bottom <= window.innerHeight;
    }
};

// API Manager
const API = {
    /**
     * Wykonuje zapytanie API
     */
    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    /**
     * Wysyła wiadomość do AI
     */
    async sendMessage(provider, model, message, conversationId) {
        return this.request(window.DemokratyzatorAI.apiEndpoints.chat, {
            method: 'POST',
            body: JSON.stringify({
                provider,
                model,
                message,
                conversation_id: conversationId
            })
        });
    },

    /**
     * Sprawdza status proxy
     */
    async checkProxyStatus() {
        try {
            return await this.request(window.DemokratyzatorAI.apiEndpoints.proxyStatus);
        } catch (error) {
            return { status: 'offline', error: error.message };
        }
    },

    /**
     * Pobiera dostępne modele dla providera
     */
    async getAvailableModels(provider) {
        try {
            return await this.request(`${window.DemokratyzatorAI.apiEndpoints.models}/${provider}`);
        } catch (error) {
            console.error(`Błąd pobierania modeli dla ${provider}:`, error);
            return { models: [] };
        }
    }
};

// Storage Manager
const Storage = {
    /**
     * Zapisuje dane w localStorage
     */
    save(key, data) {
        try {
            localStorage.setItem(`demokratyzator_${key}`, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Błąd zapisywania danych:', error);
            return false;
        }
    },

    /**
     * Odczytuje dane z localStorage
     */
    load(key, defaultValue = null) {
        try {
            const data = localStorage.getItem(`demokratyzator_${key}`);
            return data ? JSON.parse(data) : defaultValue;
        } catch (error) {
            console.error('Błąd odczytywania danych:', error);
            return defaultValue;
        }
    },

    /**
     * Usuwa dane z localStorage
     */
    remove(key) {
        try {
            localStorage.removeItem(`demokratyzator_${key}`);
            return true;
        } catch (error) {
            console.error('Błąd usuwania danych:', error);
            return false;
        }
    },

    /**
     * Czyści wszystkie dane aplikacji
     */
    clear() {
        try {
            const keys = Object.keys(localStorage).filter(key => 
                key.startsWith('demokratyzator_')
            );
            keys.forEach(key => localStorage.removeItem(key));
            return true;
        } catch (error) {
            console.error('Błąd czyszczenia danych:', error);
            return false;
        }
    }
};

// Theme Manager
const Theme = {
    /**
     * Inicjalizuje motyw
     */
    init() {
        const savedTheme = Storage.load('theme', 'dark');
        this.setTheme(savedTheme);
    },

    /**
     * Ustawia motyw
     */
    setTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        Storage.save('theme', theme);
        window.DemokratyzatorAI.settings.darkMode = theme === 'dark';
    },

    /**
     * Przełącza motyw
     */
    toggle() {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        return newTheme;
    },

    /**
     * Pobiera aktualny motyw
     */
    getCurrent() {
        return document.documentElement.getAttribute('data-bs-theme') || 'dark';
    }
};

// Event Manager
const Events = {
    listeners: new Map(),

    /**
     * Dodaje nasłuchiwacz zdarzeń
     */
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    },

    /**
     * Usuwa nasłuchiwacz zdarzeń
     */
    off(event, callback) {
        if (!this.listeners.has(event)) return;
        
        const callbacks = this.listeners.get(event);
        const index = callbacks.indexOf(callback);
        if (index > -1) {
            callbacks.splice(index, 1);
        }
    },

    /**
     * Emituje zdarzenie
     */
    emit(event, data = null) {
        if (!this.listeners.has(event)) return;
        
        this.listeners.get(event).forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Błąd w callback dla zdarzenia ${event}:`, error);
            }
        });
    }
};

// Loading Manager
const Loading = {
    activeLoaders: new Set(),

    /**
     * Pokazuje loader na elemencie
     */
    show(element, text = 'Ładowanie...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;
        
        element.classList.add('loading');
        element.setAttribute('data-loading-text', text);
        this.activeLoaders.add(element);
    },

    /**
     * Ukrywa loader
     */
    hide(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;
        
        element.classList.remove('loading');
        element.removeAttribute('data-loading-text');
        this.activeLoaders.delete(element);
    },

    /**
     * Ukrywa wszystkie loadery
     */
    hideAll() {
        this.activeLoaders.forEach(element => {
            this.hide(element);
        });
    }
};

// Inicjalizacja aplikacji
document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 Demokratyzator AI inicjalizuje się...');
    
    // Inicjalizuj motyw
    Theme.init();
    
    // Inicjalizuj ikony Feather
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Załaduj ustawienia użytkownika
    const savedSettings = Storage.load('settings', {});
    Object.assign(window.DemokratyzatorAI.settings, savedSettings);
    
    // Obsługa globalnych skrótów klawiszowych
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K - szybkie wyszukiwanie
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], #modelSearch');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + / - przełącz motyw
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            Theme.toggle();
            Utils.showToast(`Motyw zmieniony na ${Theme.getCurrent()}`, 'info', 2000);
        }
    });
    
    // Obsługa offline/online
    window.addEventListener('online', function() {
        Utils.showToast('Połączenie z internetem zostało przywrócone', 'success');
    });
    
    window.addEventListener('offline', function() {
        Utils.showToast('Brak połączenia z internetem', 'warning');
    });
    
    // Obsługa błędów JavaScript
    window.addEventListener('error', function(e) {
        if (window.DemokratyzatorAI.debug) {
            console.error('Błąd JavaScript:', e.error);
            Utils.showToast('Wystąpił błąd aplikacji', 'error');
        }
    });
    
    // Emituj zdarzenie gotowości
    Events.emit('app:ready');
    
    console.log('✅ Demokratyzator AI gotowy do pracy!');
});

// Obsługa zamykania strony
window.addEventListener('beforeunload', function(e) {
    // Zapisz ustawienia
    Storage.save('settings', window.DemokratyzatorAI.settings);
    
    // Ukryj wszystkie loadery
    Loading.hideAll();
});

// Eksportuj globalne API
window.DemokratyzatorAI.Utils = Utils;
window.DemokratyzatorAI.API = API;
window.DemokratyzatorAI.Storage = Storage;
window.DemokratyzatorAI.Theme = Theme;
window.DemokratyzatorAI.Events = Events;
window.DemokratyzatorAI.Loading = Loading;
