document.addEventListener('DOMContentLoaded', () => {
    const heroSection = document.getElementById('heroSection');
    const searchForm = document.getElementById('searchForm');
    const topicInput = document.getElementById('topicInput');
    const initialLoader = document.getElementById('initialLoader');
    const workspace = document.getElementById('workspace');
    const activeTopicTitle = document.getElementById('activeTopicTitle');
    const introContent = document.getElementById('introContent');
    const githubCard = document.getElementById('githubCard');
    const resetBtn = document.getElementById('resetBtn');

    const resultModal = document.getElementById('resultModal');
    const modalBackdrop = document.getElementById('modalBackdrop');
    const modalClose = document.getElementById('modalClose');
    const modalTitle = document.getElementById('modalTitle');
    const modalIcon = document.getElementById('modalIcon');
    const modalLoader = document.getElementById('modalLoader');
    const modalContainer = document.getElementById('modalContainer');

    let currentTopic = '';
    let isTechTopic = false;

    const actionMeta = {
        'detailed': { title: 'Detailed Explanation', icon: '<i class="fa-solid fa-book-open-reader"></i>' },
        'web': { title: 'Web Articles & Docs', icon: '<i class="fa-solid fa-globe"></i>' },
        'youtube': { title: 'YouTube Tutorials', icon: '<i class="fa-brands fa-youtube" style="color:#ef4444;"></i>' },
        'github': { title: 'GitHub Repositories', icon: '<i class="fa-brands fa-github"></i>' },
        'pdf': { title: 'PDF Documents & Papers', icon: '<i class="fa-solid fa-file-pdf" style="color:#ea580c;"></i>' },
        'book': { title: 'Books & Textbooks', icon: '<i class="fa-solid fa-book-bookmark" style="color:#2563eb;"></i>' },
        'study-plan': { title: 'Custom 4-Week Study Plan', icon: '<i class="fa-solid fa-calendar-check" style="color:#9333ea;"></i>' },
        'ask': { title: 'Ask Course Assistant', icon: '<i class="fa-solid fa-circle-question" style="color:#16a34a;"></i>' }
    };

    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const topic = chip.getAttribute('data-topic');
            if (topic) {
                topicInput.value = topic;
                handleTopicSubmit(topic);
            }
        });
    });

    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const topic = topicInput.value.trim();
        if (topic) {
            handleTopicSubmit(topic);
        }
    });

    resetBtn.addEventListener('click', () => {
        workspace.classList.add('hidden');
        heroSection.classList.remove('hidden');
        topicInput.value = '';
        topicInput.focus();
    });

    modalClose.addEventListener('click', closeModal);
    modalBackdrop.addEventListener('click', closeModal);

    function closeModal() {
        resultModal.classList.add('hidden');
    }

    async function handleTopicSubmit(topic) {
        currentTopic = topic;
        heroSection.classList.add('hidden');
        initialLoader.classList.remove('hidden');
        workspace.classList.add('hidden');

        try {
            const res = await fetch('/api/intro', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: currentTopic })
            });

            if (!res.ok) {
                throw new Error('Failed to generate intro.');
            }

            const data = await res.json();
            activeTopicTitle.textContent = data.topic;
            introContent.innerHTML = marked.parse(data.introduction);
            isTechTopic = data.is_tech;

            if (isTechTopic) {
                githubCard.classList.remove('hidden');
            } else {
                githubCard.classList.add('hidden');
            }

            initialLoader.classList.add('hidden');
            workspace.classList.remove('hidden');
        } catch (err) {
            alert('Error creating introduction: ' + err.message);
            initialLoader.classList.add('hidden');
            heroSection.classList.remove('hidden');
        }
    }

    document.addEventListener('click', async (e) => {
        const card = e.target.closest('.action-card');
        if (!card) return;

        const action = card.getAttribute('data-action');
        if (!action) return;

        if (!currentTopic) {
            let topic = topicInput.value.trim();
            if (!topic) {
                topic = 'Machine Learning';
                topicInput.value = topic;
            }
            await handleTopicSubmit(topic);
        }

        openActionModal(action);
    });

    async function openActionModal(action) {
        const meta = actionMeta[action] || { title: 'Resource', icon: '<i class="fa-solid fa-magnifying-glass"></i>' };
        modalTitle.textContent = meta.title;
        modalIcon.innerHTML = meta.icon;
        modalContainer.innerHTML = '';
        modalLoader.classList.remove('hidden');
        resultModal.classList.remove('hidden');

        try {
            if (action === 'detailed') {
                const res = await fetch('/api/detailed', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: currentTopic })
                });
                const data = await res.json();
                modalContainer.innerHTML = marked.parse(data.content);
            } 
            else if (action === 'study-plan') {
                const res = await fetch('/api/study-plan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: currentTopic })
                });
                const data = await res.json();
                modalContainer.innerHTML = marked.parse(data.plan);
            } 
            else if (action === 'ask') {
                renderQAInterface();
            } 
            else {
                const res = await fetch('/api/resources', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: currentTopic, kind: action })
                });
                const data = await res.json();
                renderResourceList(data.items);
            }
        } catch (err) {
            modalContainer.innerHTML = `<div class="error-msg">⚠️ Unable to fetch details. ${err.message}</div>`;
        } finally {
            modalLoader.classList.add('hidden');
        }
    }

    function renderResourceList(items) {
        if (!items || items.length === 0) {
            modalContainer.innerHTML = `<p>No specific resources found for this topic.</p>`;
            return;
        }

        let html = `<div class="resource-list">`;
        items.forEach(item => {
            let descHtml = '';
            if (item.description) {
                const parts = item.description.split(/(?<=[.!?])\s+/).filter(s => s.trim().length > 8);
                if (parts.length > 1) {
                    descHtml = `<ul class="resource-bullets">${parts.slice(0, 3).map(s => `<li>${s.trim()}</li>`).join('')}</ul>`;
                } else {
                    descHtml = `<p class="resource-desc">${item.description}</p>`;
                }
            }

            html += `
                <div class="resource-item">
                    <div class="resource-info">
                        <h5>${item.title}</h5>
                        ${descHtml}
                        ${item.extra ? `<div class="resource-extra">${item.extra}</div>` : ''}
                    </div>
                    <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="resource-link">
                        Open <i class="fa-solid fa-arrow-up-right-from-square"></i>
                    </a>
                </div>
            `;
        });
        html += `</div>`;
        modalContainer.innerHTML = html;
    }

    function renderQAInterface() {
        modalContainer.innerHTML = `
            <div class="qa-form">
                <input type="text" id="qaInput" placeholder="Ask any doubt about ${currentTopic}..." />
                <button id="qaSubmit">Ask Tutor</button>
            </div>
            <div id="qaAnswer" class="markdown-body"></div>
        `;

        const qaInput = document.getElementById('qaInput');
        const qaSubmit = document.getElementById('qaSubmit');
        const qaAnswer = document.getElementById('qaAnswer');

        qaSubmit.addEventListener('click', async () => {
            const question = qaInput.value.trim();
            if (!question) return;

            qaAnswer.innerHTML = '<div class="spinner"></div><p>Thinking...</p>';
            try {
                const res = await fetch('/api/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: currentTopic, question: question })
                });
                const data = await res.json();
                qaAnswer.innerHTML = marked.parse(data.answer);
            } catch (err) {
                qaAnswer.innerHTML = `<p style="color: #ff4d4d;">Error: ${err.message}</p>`;
            }
        });
    }
});
