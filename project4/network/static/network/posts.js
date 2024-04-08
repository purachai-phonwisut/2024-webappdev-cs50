document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.onclick = function() {
            const postId = this.getAttribute('data-postid');
            const contentDiv = document.getElementById(`post-content-${postId}`);
            const content = contentDiv.innerText;

            contentDiv.innerHTML = `
                <textarea id="edit-text-${postId}" rows="4">${content}</textarea>
                <button class="save-btn" data-postid="${postId}">Save</button>
            `;

            document.querySelector(`.save-btn[data-postid="${postId}"]`).onclick = function() {
                const newText = document.getElementById(`edit-text-${postId}`).value;

                fetch(`/post/${postId}/edit`, {
                    method: 'POST',
                    body: JSON.stringify({
                        content: newText,
                    }),
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        contentDiv.innerHTML = newText;
                    } else {
                        alert("There was an error saving the post.");
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            };
        };
    });

    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.getAttribute('data-postid');
            fetch('/like', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    post_id: postId,
                }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === "ok") {
                    const likeCountSpan = document.getElementById(`like-count-${postId}`);
                    let likeCount = parseInt(likeCountSpan.innerText, 10);
                    likeCount = data.action === 'liked' ? likeCount + 1 : likeCount - 1;
                    likeCountSpan.innerText = likeCount.toString();
                    this.textContent = data.action === 'liked' ? 'Unlike' : 'Like';
                } else {
                    alert("There was an error processing the like.");
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }); 

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const likeButton = document.getElementById('not-authenticated');

    likeButton.addEventListener('click', function() {
        alert('Please log in before liking a post.');
    });
});
