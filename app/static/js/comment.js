
async function getCommentData(){
    const response = await fetch('/api/comments');
    return response.json();
}

function loadTable(comments){
    const table = document.querySelector('#result');
    for(let comment of comments){
        table.innerHTML += `<tr>
            <td>${comment.comment_id}</td>
            <td>${comment.post_id}</td>
            <td>${comment.user_id}</td>
            <td>${comment.content}</td>
        </tr>`;
    }
}

async function main(){
    const comments = await getCommentData();
    loadTable(comments);
}

main();
