let isListening = false;
    let chatHistory = [];
    let cpuChart, ramChart, gpuChart;
    let recognition;
    let speakEnabled = false;
    let conversationModeEnabled = false;

    const statusText = document.getElementById('statusText');
    const statusIcon = document.getElementById('statusIcon');
    const chatContainer = document.getElementById('chatContainer');
    const messageInput = document.getElementById('messageInput');
    const speakToggle = document.getElementById('speakToggle');
    const conversationModeToggle = document.getElementById('conversationModeToggle');
    const customizeModal = document.getElementById('customizeModal');
    const closeCustomizeModalBtn = document.getElementById('closeCustomizeModal');
    const themeButtons = document.querySelectorAll('.theme-btn');
    const modelSelect = document.getElementById('modelSelect');
    const setModelBtn = document.getElementById('setModelBtn');
    const contextFileInput = document.getElementById('contextFileInput');
    const chatHistoryInput = document.getElementById('chatHistoryInput');

    const contextModal = document.getElementById('contextModal');
    const closeContextModalBtn = document.getElementById('closeContextModal');
    const contextFileDisplay = document.getElementById('contextFileDisplay');
    const typedContextInput = document.getElementById('typedContextInput');
    const chatSummaryDisplay = document.getElementById('chatSummaryDisplay');
    const saveTypedContextBtn = document.getElementById('saveTypedContextBtn');
    const clearTypedContextBtn = document.getElementById('clearTypedContextBtn');
    const clearFileContextBtn = document.getElementById('clearFileContextBtn');
    const clearAllContextBtn = document.getElementById('clearAllContextBtn');
    const summarizeChatBtn = document.getElementById('summarizeChatBtn');

    const thinkingAnimation = document.getElementById('thinking-animation');

    // --- State Management ---
    function setStatus(status) {
        switch (status) {
            case 'listening':
                isListening = true;
                statusText.textContent = 'Listening...';
                statusIcon.src = 'img/listening.svg';
                thinkingAnimation.style.display = 'none';
                break;
            case 'thinking':
                isListening = false;
                statusText.textContent = 'Thinking...';
                statusIcon.src = 'img/thinking.svg';
                thinkingAnimation.style.display = 'block';
                break;
            case 'idle':
            default:
                isListening = false;
                statusText.textContent = 'Idle';
                statusIcon.src = 'img/idle.svg';
                thinkingAnimation.style.display = 'none';
                break;
        }
    }

    // --- System Stats ---
    async function updateSystemStats() {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/system_stats');
            if (!response.ok) return;

            const stats = await response.json();

            if (stats.gpu_error) {
                showModal(stats.gpu_error, () => {}, true);
            }

            updateChart(cpuChart, stats.cpu);
            updateChart(ramChart, stats.ram);
            updateChart(gpuChart, stats.gpu);

        } catch (error) {
            console.error("Error fetching system stats:", error);
        }
    }

    // --- Charting ---
    function createChart(ctx, label, color) {
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array(20).fill(''),
                datasets: [{
                    label: label,
                    data: Array(20).fill(0),
                    borderColor: color,
                    backgroundColor: color + '33',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        display: false
                    },
                    x: {
                        display: false
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    function updateChart(chart, value) {
        chart.data.datasets[0].data.shift();
        chart.data.datasets[0].data.push(value);
        chart.update('none');
    }

    // --- Chat Functionality ---
    function handleKeyPress(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    }

    async function sendMessage(messageOverride) {
        const message = messageOverride || messageInput.value.trim();
        if (!message) return;

        addMessageToChat(message, 'user');
        messageInput.value = '';
        setStatus('thinking');

        try {
            const response = await callYourLLM(message);
            addMessageToChat(response, 'ai');
            if (speakEnabled) {
                speak(response);
            }
        } catch (error) {
            console.error("LLM Error:", error);
            addMessageToChat('Sorry, I encountered an error. Please try again.', 'ai');
        } finally {
            setStatus(isListening ? 'listening' : 'idle');
        }
    }

    function addMessageToChat(message, sender, save = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender === 'user' ? 'user-message' : 'ai-message'}`;

        const messageContent = document.createElement('p');
        messageContent.textContent = message;

        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();

        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(timestamp);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        if (save) {
            chatHistory.push({ message, sender, timestamp: new Date().toISOString() });
            localStorage.setItem('jarvisChatHistory', JSON.stringify(chatHistory));
        }
    }

    // --- LLM Integration ---
    async function callYourLLM(message) {
        const response = await fetch('http://127.0.0.1:5000/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory.slice(0, -1)
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Failed to parse error response from server.' }));
            console.error('API Error:', errorData);
            throw new Error(errorData.error || 'An unknown network error occurred.');
        }

        const data = await response.json();
        return data.response;
    }

    // --- Speech Recognition and Synthesis ---
    function listen() {
        if (isListening && !conversationModeEnabled) {
            recognition.stop();
            return;
        }

        try {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = () => {
                setStatus('listening');
            };

            recognition.onresult = (event) => {
                const speechResult = event.results[0][0].transcript;
                sendMessage(speechResult);
            };

            recognition.onspeechend = () => {
                if (conversationModeEnabled) {
                    // If in conversation mode, restart listening after a short delay
                    setStatus('idle'); // Briefly show idle before restarting listen
                    setTimeout(() => {
                        if (conversationModeEnabled) { // Check again in case mode was toggled off
                            listen();
                        }
                    }, 500); 
                } else {
                    setStatus('idle');
                }
            };

            recognition.onerror = (event) => {
                showModal(`Error occurred in recognition: ${event.error}`, () => {}, true);
                setStatus('idle');
                if (conversationModeEnabled) {
                    // If in conversation mode, try to restart listening on error
                    setTimeout(() => {
                        if (conversationModeEnabled) {
                            listen();
                        }
                    }, 1000);
                }
            };

            recognition.start();
        } catch (e) {
            showModal("Speech recognition is not supported by your browser. Please use Chrome or another supported browser.", () => {}, true);
        }
    }

    async function speak(text) {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/speak', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Failed to parse error response from server.' }));
                showModal(`ElevenLabs API Error: ${errorData.error || response.statusText}`, () => {}, true);
                return;
            }

            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            audio.play();

            return new Promise(resolve => {
                audio.onended = resolve;
            });

        } catch (error) {
            console.error("Error speaking text:", error);
            showModal(`Error playing audio: ${error.message}`, () => {}, true);
        }
    }

    speakToggle.addEventListener('click', () => {
        speakEnabled = !speakEnabled;
        speakToggle.style.backgroundColor = speakEnabled ? '#10b981' : '#6366f1';
        speakToggle.textContent = speakEnabled ? 'SPEAKING' : 'SPEAK';
    });

    conversationModeToggle.addEventListener('click', () => {
        conversationModeEnabled = !conversationModeEnabled;
        conversationModeToggle.style.backgroundColor = conversationModeEnabled ? '#10b981' : '#6366f1';
        conversationModeToggle.textContent = conversationModeEnabled ? 'CONVERSATION ON' : 'CONVERSATION OFF';

        if (conversationModeEnabled) {
            listen(); // Start listening immediately when conversation mode is enabled
        } else {
            if (isListening) {
                recognition.stop();
            }
            setStatus('idle');
        }
    });

    // --- Sidebar Controls ---
    function openContext() {
        contextModal.style.display = 'flex';
        loadContextData();
    }

    closeContextModalBtn.addEventListener('click', () => {
        contextModal.style.display = 'none';
    });

    async function loadContextData() {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/context');
            const data = await response.json();
            contextFileDisplay.textContent = data.file_context || 'No file context loaded.';
            typedContextInput.value = data.typed_context || '';
            chatSummaryDisplay.textContent = data.chat_summary || 'Chat summary not yet available.';
        } catch (error) {
            console.error("Error loading context data:", error);
            showModal("Failed to load context data from the server.", () => {}, true);
        }
    }

    clearFileContextBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/clear_file_context', { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                showModal('File context cleared successfully.', () => {}, true);
                loadContextData(); // Refresh display
            } else {
                showModal(`Failed to clear file context: ${data.error}`, () => {}, true);
            }
        } catch (error) {
            console.error("Error clearing file context:", error);
            showModal("Error communicating with the server to clear file context.", () => {}, true);
        }
    });

    saveTypedContextBtn.addEventListener('click', async () => {
        const context = typedContextInput.value;
        try {
            const response = await fetch('http://127.0.0.1:5000/api/save_typed_context', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ context: context })
            });
            const data = await response.json();
            if (data.success) {
                showModal('Typed context saved successfully.', () => {}, true);
            } else {
                showModal(`Failed to save typed context: ${data.error}`, () => {}, true);
            }
        } catch (error) {
            console.error("Error saving typed context:", error);
            showModal("Error communicating with the server to save typed context.", () => {}, true);
        }
    });

    clearTypedContextBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/clear_typed_context', { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                showModal('Typed context cleared successfully.', () => {}, true);
                typedContextInput.value = ''; // Clear the textarea
            } else {
                showModal(`Failed to clear typed context: ${data.error}`, () => {}, true);
            }
        } catch (error) {
            console.error("Error clearing typed context:", error);
            showModal("Error communicating with the server to clear typed context.", () => {}, true);
        }
    });

    clearAllContextBtn.addEventListener('click', async () => {
        showModal('Are you sure you want to clear all context? This action cannot be undone.', async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/api/clear_all_context', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    showModal('All context has been cleared.', () => {}, true);
                    loadContextData(); // Refresh the modal display
                } else {
                    showModal(`Failed to clear all context: ${data.error}`, () => {}, true);
                }
            } catch (error) {
                console.error("Error clearing all context:", error);
                showModal("An error occurred while communicating with the server.", () => {}, true);
            }
        });
    });

    summarizeChatBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/summarize_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ history: chatHistory })
            });
            const data = await response.json();
            if (data.success) {
                chatSummaryDisplay.textContent = data.summary;
                showModal('Chat summary has been updated.', () => {}, true);
            } else {
                showModal(`Failed to summarize chat: ${data.error}`, () => {}, true);
            }
        } catch (error) {
            console.error("Error summarizing chat:", error);
            showModal("An error occurred while communicating with the server.", () => {}, true);
        }
    });

    function deleteChat() {
        showModal('Are you sure you want to permanently delete the chat history?', () => {
            chatContainer.innerHTML = '';
            chatHistory = [];
            localStorage.removeItem('jarvisChatHistory');
            addMessageToChat("Chat cleared. How can I assist you?", 'ai', true);
        });
    }

    function saveChat() {
        if (chatHistory.length === 0) {
            showModal("There is no chat history to save.", () => {}, true);
            return;
        }
        const dataStr = JSON.stringify(chatHistory, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        const exportFileDefaultName = `jarvis_chat_${new Date().getTime()}.json`;

        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }

    function loadChat() {
        console.log('loadChat called');
        chatHistoryInput.click();
    }

    function addContext() {
        console.log('addContext called');
        contextFileInput.click();
    }

    function customize() {
        customizeModal.style.display = 'flex';
        loadModels();
        loadTheme();
    }

    function resetSystem() {
        showModal('Are you sure you want to reset the system? This will clear the chat and reload the application.', () => {
            localStorage.removeItem('jarvisChatHistory');
            location.reload();
        });
    }

    function exitApp() {
        showModal('Are you sure you want to exit J.A.R.V.I.S?', () => {
            window.close();
        });
    }

    // --- Modal ---
    function showModal(text, onConfirm, isAlert = false) {
        const modal = document.getElementById('infoModal');
        const modalText = document.getElementById('modalText');
        const confirmBtn = document.getElementById('modalConfirm');
        const cancelBtn = document.getElementById('modalCancel');

        modalText.textContent = text;

        if (isAlert) {
            confirmBtn.style.display = 'none';
            cancelBtn.textContent = 'Close';
        } else {
            confirmBtn.style.display = 'inline-flex';
            cancelBtn.textContent = 'Cancel';
        }

        modal.style.display = 'flex';

        const confirmHandler = () => {
            onConfirm();
            closeModal();
        };

        const cancelHandler = () => {
            closeModal();
        };

        const closeModal = () => {
            modal.style.display = 'none';
            confirmBtn.removeEventListener('click', confirmHandler);
            cancelBtn.removeEventListener('click', cancelHandler);
        }

        confirmBtn.addEventListener('click', confirmHandler);
        cancelBtn.addEventListener('click', cancelHandler);
    }

    // --- Initialization ---
    function loadChatHistory() {
        const savedHistory = localStorage.getItem('jarvisChatHistory');
        if (savedHistory && savedHistory.length > 2) { // Check for non-empty array
            chatHistory = JSON.parse(savedHistory);
            chatContainer.innerHTML = '';
            chatHistory.forEach(item => {
                addMessageToChat(item.message, item.sender, false);
            });
        } else {
            addMessageToChat("Hello! I'm J.A.R.V.I.S, your AI assistant. How can I help you today?", 'ai');
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        const contextFileInput = document.getElementById('contextFileInput');
        const chatHistoryInput = document.getElementById('chatHistoryInput');

        cpuChart = createChart(document.getElementById('cpuChart').getContext('2d'), 'CPU', '#4facfe');
        ramChart = createChart(document.getElementById('ramChart').getContext('2d'), 'RAM', '#a855f7');
        gpuChart = createChart(document.getElementById('gpuChart').getContext('2d'), 'GPU', '#10b981');

        loadChatHistory();
        setStatus('idle');
        setInterval(updateSystemStats, 1000);
        messageInput.focus();

        loadModels();
        loadTheme();
    });

    closeCustomizeModalBtn.addEventListener('click', () => {
        customizeModal.style.display = 'none';
    });

    themeButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const theme = event.target.dataset.theme;
            setTheme(theme);
        });
    });

    setModelBtn.addEventListener('click', async () => {
        const selectedModel = modelSelect.value;
        try {
            const response = await fetch('http://127.0.0.1:5000/api/set_model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model_key: selectedModel })
            });
            const data = await response.json();
            if (data.success) {
                showModal(`LLM model successfully set to ${selectedModel}.`, () => {}, true);
                localStorage.setItem('jarvisLLMModel', selectedModel);
            } else {
                showModal(`Failed to set LLM model: ${data.error}`, () => {}, true);
            }
        } catch (error) {
            console.error("Error setting LLM model:", error);
            showModal("Error communicating with the server to set the LLM model.", () => {}, true);
        }
    });

    chatHistoryInput.addEventListener('change', async () => {
        if (chatHistoryInput.files.length === 0) {
            return; // No file selected
        }
        const file = chatHistoryInput.files[0];
        const formData = new FormData();
        formData.append('context_file', file);

        try {
            const response = await fetch('http://127.0.0.1:5000/api/load_context', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (data.success && data.history) {
                chatHistory = data.history;
                localStorage.setItem('jarvisChatHistory', JSON.stringify(chatHistory));
                loadChatHistory(); // Reload the chat display
                showModal(`Chat history loaded successfully from ${file.name}.`, () => {}, true);
            } else {
                showModal(`Failed to load chat history: ${data.error || 'Invalid file format.'}`, () => {}, true);
            }
        } catch (error) {
            console.error("Error loading chat history:", error);
            showModal("Error communicating with the server to load the file.", () => {}, true);
        }
    });

    async function loadModels() {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/models');
            if (!response.ok) {
                showModal("Failed to load LLM models from the server.", () => {}, true);
                return;
            }
            const models = await response.json();
            modelSelect.innerHTML = '';
            for (const key in models) {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = key;
                modelSelect.appendChild(option);
            }
            const savedModel = localStorage.getItem('jarvisLLMModel');
            if (savedModel) {
                modelSelect.value = savedModel;
            }
        } catch (error) {
            console.error("Error loading LLM models:", error);
            showModal("Error fetching LLM models from the server.", () => {}, true);
        }
    }

    function setTheme(theme) {
        document.body.className = ''; // Clear existing themes
        document.body.classList.add(theme);
        localStorage.setItem('jarvisTheme', theme);
        themeButtons.forEach(btn => {
            if (btn.dataset.theme === theme) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    function loadTheme() {
        const savedTheme = localStorage.getItem('jarvisTheme');
        if (savedTheme) {
            setTheme(savedTheme);
        } else {
            setTheme('dark'); // Default theme
        }
    }