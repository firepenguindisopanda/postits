async function loadFeed() {
    const container = document.getElementById('feed-container');
    container.innerHTML = '<div class="text-center py-5 text-muted">Loading posts...</div>';

    try {
        const response = await fetch('/postits/api/feed');
        const posts = await response.json();

        if (posts.length === 0) {
            container.innerHTML = `
                <div class="empty-feed">
                    <div class="material-symbols-outlined">forum</div>
                    <h5>No posts yet</h5>
                    <p class="text-muted">Be the first to share something!</p>
                </div>`;
            return;
        }

        container.innerHTML = '';
        for (const post of posts) {
            container.appendChild(createPostCard(post));
        }
    } catch (err) {
        container.innerHTML = '<div class="text-center py-5 text-danger">Failed to load posts. Try again later.</div>';
    }
}

function timeAgo(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return minutes + 'm ago';
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return hours + 'h ago';
    const days = Math.floor(hours / 24);
    if (days < 7) return days + 'd ago';
    return date.toLocaleDateString();
}

function createPostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';
    card.dataset.postId = post.post_id;

    card.innerHTML = `
        <div class="post-header">
            <div class="avatar-placeholder" style="width:32px;height:32px;font-size:14px;">${post.username[0].toUpperCase()}</div>
            <div>
                <span class="post-author">u/${post.username}</span>
                <span class="post-time">${timeAgo(post.created_at)}</span>
            </div>
        </div>
        <div class="post-content">${escapeHtml(post.content)}</div>
        <div class="post-actions">
            <button class="comment-toggle" onclick="toggleComments(this, ${post.post_id})">
                <span class="material-symbols-outlined" style="font-size:18px;">chat_bubble_outline</span>
                Comments (${post.comment_count})
            </button>
        </div>
        <div class="comments-section" id="comments-${post.post_id}">
            <div id="comments-list-${post.post_id}"></div>
            <div class="comment-form">
                <input type="text" id="comment-input-${post.post_id}" placeholder="Write a comment..." maxlength="500">
                <button class="btn btn-primary btn-sm" onclick="postComment(${post.post_id})">Post</button>
            </div>
        </div>
    `;

    return card;
}

async function toggleComments(btn, postId) {
    const section = document.getElementById('comments-' + postId);

    if (section.classList.contains('expanded')) {
        section.classList.remove('expanded');
        return;
    }

    section.classList.add('expanded');
    const list = document.getElementById('comments-list-' + postId);

    if (list.hasChildNodes()) return;

    list.innerHTML = '<div class="text-muted py-2" style="font-size:13px;">Loading comments...</div>';

    try {
        const response = await fetch('/postits/api/posts/' + postId + '/comments');
        const comments = await response.json();
        list.innerHTML = '';

        if (comments.length === 0) {
            list.innerHTML = '<div class="text-muted py-2" style="font-size:13px;">No comments yet. Be the first!</div>';
            return;
        }

        for (const comment of comments) {
            const div = document.createElement('div');
            div.className = 'comment-item';
            div.innerHTML = `
                <div>
                    <span class="comment-author">u/${escapeHtml(comment.username)}</span>
                    <span class="comment-time">${timeAgo(comment.created_at)}</span>
                </div>
                <div class="comment-text">${escapeHtml(comment.content)}</div>
            `;
            list.appendChild(div);
        }
    } catch (err) {
        list.innerHTML = '<div class="text-danger py-2" style="font-size:13px;">Failed to load comments.</div>';
    }
}

async function postComment(postId) {
    const input = document.getElementById('comment-input-' + postId);
    const content = input.value.trim();
    if (!content) return;

    input.disabled = true;

    try {
        const response = await fetch('/postits/api/comments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content, post_id: postId }),
        });

        if (!response.ok) {
            const err = await response.json();
            showToast('Error', err.detail || 'Failed to post comment', 'danger');
            input.disabled = false;
            return;
        }

        input.value = '';
        input.disabled = false;

        const list = document.getElementById('comments-list-' + postId);
        list.innerHTML = '';
        const btn = document.querySelector(`.post-card[data-post-id="${postId}"] .comment-toggle`);
        if (btn) btn.click();
        if (btn) btn.click();
    } catch (err) {
        showToast('Error', 'Failed to post comment', 'danger');
        input.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    loadFeed();

    document.getElementById('btn-create-post').addEventListener('click', async function () {
        const textarea = document.getElementById('post-content');
        const content = textarea.value.trim();
        if (!content) return;

        this.disabled = true;
        this.textContent = 'Posting...';

        try {
            const response = await fetch('/postits/api/posts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: content }),
            });

            if (!response.ok) {
                const err = await response.json();
                showToast('Error', err.detail || 'Failed to create post', 'danger');
                this.disabled = false;
                this.textContent = 'Share';
                return;
            }

            textarea.value = '';
            this.disabled = false;
            this.textContent = 'Share';
            loadFeed();
            showToast('Success', 'Post created!', 'success');
        } catch (err) {
            showToast('Error', 'Failed to create post', 'danger');
            this.disabled = false;
            this.textContent = 'Share';
        }
    });
});

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(title, message, type) {
    const toastEl = document.getElementById('appToast');
    document.getElementById('toastTitle').textContent = title;
    document.getElementById('toastContent').textContent = message;
    toastEl.className = 'toast text-bg-' + type;
    const toast = bootstrap.Toast.getOrCreateInstance(toastEl);
    toast.show();
}
