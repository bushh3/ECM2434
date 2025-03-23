function goBack() {
    window.history.back();
}

// Get the CSRF token from cookies for Django
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

// URL for Django's API endpoint---------------------------------URL,,要返回以下例子的格式，return name,score,avatar--------------------------
const API_URL = "/leaderboard/api/rankings/"; 

// selfUsername is defined directly in the template

// ------------------- 模拟用户数据开始 ------------------连接完删除------------------mock users，will be delected after connection
// Mock data (used as fallback if API fails)
const mockUsers = [
    { name: "Annie", score: 50, avatar: "/static/pictures/bird.jpg" },
    { name: "Bob", score: 45, avatar: "/static/pictures/bird.jpg" },
    { name: "Charlie", score: 40, avatar: "/static/pictures/bird.jpg" },
    { name: "Diana", score: 32, avatar: "/static/pictures/bird.jpg" },
    { name: "Edward", score: 24, avatar: "/static/pictures/bird.jpg" },
    { name: "Fiona", score: 15, avatar: "/static/pictures/bird.jpg" },
    { name: "George", score: 13, avatar: "/static/pictures/bird.jpg" },
    { name: "Helen", score: 13, avatar: "/static/pictures/bird.jpg" },
    { name: "Ian", score: 13, avatar: "/static/pictures/bird.jpg" },
    { name: "Jack", score: 9, avatar: "/static/pictures/bird.jpg" },
    { name: "Kevin", score: 5, avatar: "/static/pictures/bird.jpg" },
    { name: "Laura", score: 3, avatar: "/static/pictures/bird.jpg" },
    { name: "Mike", score: 2, avatar: "/static/pictures/bird.jpg" },
    { name: "Nancy", score: 1, avatar: "/static/pictures/bird.jpg" },
    { name: selfUsername, score: 5, avatar: "/static/pictures/bird.jpg" }
];
// ------------------- 模拟用户数据结束 ------------------

// Store global user data and ranking data for click display
let globalUserData = [];
let globalRankingsData = [];

// Fetch leaderboard data with loading indicators
async function fetchLeaderboard() {
    // Show loading state
    document.getElementById("rankingList").innerHTML = `
        <li class="loading">
            <div class="loading-spinner"></div>
            <span>Loading rankings...</span>
        </li>`;
    
    try {
        // Try to fetch from the API with CSRF token for Django----------------------------------连接---connection------------------
        const response = await fetch(API_URL, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest', 
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        // Check if response is ok
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }
        
        const users = await response.json();
        globalUserData = [...users]; // Store global data
        renderLeaderboard(users);
    } catch (error) {
        console.error("Failed to fetch leaderboard data", error);
        
        // ------------------- 使用模拟数据的部分开始 ------------------连接完删除-----------mock users，will be delected after connection
        console.log("Using mock data instead");
        // Add a small delay to simulate API call
        setTimeout(() => {
            globalUserData = [...mockUsers]; // Store global data
            renderLeaderboard(mockUsers);
        }, 800);
        // ------------------- 使用模拟数据的部分结束 ------------------
    }
}

// Calculate actual rank for each user
function calculateRankings(users) {
    let rankings = [];
    let currentRank = 1;
    let currentScore = null;
    let sameRankCount = 0;
    
    const sortedUsers = [...users].sort((a, b) => b.score - a.score);
    
    sortedUsers.forEach((user, index) => {
        if (index === 0) {
            currentScore = user.score;
            rankings.push({
                user: user,
                rank: currentRank
            });
            sameRankCount = 1;
        } else {
            if (user.score === currentScore) {
                rankings.push({
                    user: user,
                    rank: currentRank
                });
                sameRankCount++;
            } else {
                currentRank += sameRankCount;
                currentScore = user.score;
                rankings.push({
                    user: user,
                    rank: currentRank
                });
                sameRankCount = 1;
            }
        }
    });
    globalRankingsData = [...rankings];
    return rankings;
}

// Show tied users modal
function showTiedUsersModal(rank) {
    // Get all users of the same rank
    const tiedUsers = globalRankingsData.filter(item => item.rank === rank);
    
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'tied-users-modal';
    
    // Create modal content
    let modalContent = `
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h3>Rank ${rank} Users</h3>
            <div class="tied-users-list">
    `;
    
    // Add user list
    tiedUsers.forEach(item => {
        // Check if current user
        const isSelf = item.user.name === selfUsername;
        const selfClass = isSelf ? 'is-self' : '';
        
        modalContent += `
            <div class="tied-user-item ${selfClass}">
                <img src="${item.user.avatar}" alt="${item.user.name}" class="tied-user-avatar">
                <span class="tied-user-name">${item.user.name} ${isSelf ? '(You)' : ''}</span>
                <span class="tied-user-score"><i class="fa fa-star star-icon"></i> ${item.user.score}</span>
            </div>
        `;
    });
    
    modalContent += `
            </div>
        </div>
    `;
    
    modal.innerHTML = modalContent;
    document.body.appendChild(modal);
    
    // Add close functionality
    const closeBtn = modal.querySelector('.close-modal');
    closeBtn.onclick = function() {
        document.body.removeChild(modal);
    };
    
    // Click outside modal to close
    window.onclick = function(event) {
        if (event.target === modal) {
            document.body.removeChild(modal);
        }
    };
}

// Update top 3 podium
function updateTopThree(users) {
    users.sort((a, b) => b.score - a.score);
    
    const rankings = calculateRankings(users);
    
    const rank1 = document.getElementById("rank1"); // First place (center)
    const rank2 = document.getElementById("rank2"); // Second place (left)
    const rank3 = document.getElementById("rank3"); // Third place (right)

    if (!rank1 || !rank2 || !rank3) {
        console.error("Could not find top three podium HTML elements!");
        return [];
    }
    
    rank1.style.display = 'none';
    rank2.style.display = 'none';
    rank3.style.display = 'none';
    
    const topRankUsers = rankings.filter(item => item.rank <= 3);
    const rankGroups = {
        1: rankings.filter(item => item.rank === 1),
        2: rankings.filter(item => item.rank === 2),
        3: rankings.filter(item => item.rank === 3)
    };
    
    // Top1
    if (rankGroups[1] && rankGroups[1].length > 0) {
        rank1.style.display = 'flex';
        const firstRankScore = rankGroups[1][0].user.score;
        
        rank1.querySelector(".rank-number").textContent = "TOP 1";
        rank1.querySelector(".score").textContent = firstRankScore;
        
        if (rankGroups[1].length > 1) {
            rank1.querySelector(".avatar-container").innerHTML = `
                <div class="tied-count-avatar">+${rankGroups[1].length}</div>
            `;
            rank1.querySelector(".name").textContent = "Tied User";
            
            rank1.onclick = function() {
                showTiedUsersModal(1);
            };
            rank1.style.cursor = 'pointer';
        } else {
            const singleUser = rankGroups[1][0].user;
            rank1.querySelector(".avatar-container").innerHTML = `
                <img class="top-avatar" src="${singleUser.avatar}" alt="${singleUser.name}">
            `;
            rank1.querySelector(".name").textContent = singleUser.name;
            rank1.onclick = null;
            rank1.style.cursor = 'default';
        }
    }
    // Top2
    if (rankGroups[2] && rankGroups[2].length > 0) {
        rank2.style.display = 'flex';
        const secondRankScore = rankGroups[2][0].user.score;
        
        rank2.querySelector(".rank-number").textContent = "TOP 2";
        rank2.querySelector(".score").textContent = secondRankScore;
        
        if (rankGroups[2].length > 1) {
            rank2.querySelector(".avatar-container").innerHTML = `
                <div class="tied-count-avatar">+${rankGroups[2].length}</div>
            `;
            rank2.querySelector(".name").textContent = "Tied User";
            
            rank2.onclick = function() {
                showTiedUsersModal(2);
            };
            rank2.style.cursor = 'pointer';
        } else {
            const singleUser = rankGroups[2][0].user;
            rank2.querySelector(".avatar-container").innerHTML = `
                <img class="top-avatar" src="${singleUser.avatar}" alt="${singleUser.name}">
            `;
            rank2.querySelector(".name").textContent = singleUser.name;
            rank2.onclick = null;
            rank2.style.cursor = 'default';
        }
    }
    // Top3
    if (rankGroups[3] && rankGroups[3].length > 0) {
        rank3.style.display = 'flex';
        const thirdRankScore = rankGroups[3][0].user.score;
        
        rank3.querySelector(".rank-number").textContent = "TOP 3";
        rank3.querySelector(".score").textContent = thirdRankScore;
        
        if (rankGroups[3].length > 1) {
            rank3.querySelector(".avatar-container").innerHTML = `
                <div class="tied-count-avatar">+${rankGroups[3].length}</div>
            `;
            rank3.querySelector(".name").textContent = "Tied User";
            
            rank3.onclick = function() {
                showTiedUsersModal(3);
            };
            rank3.style.cursor = 'pointer';
        } else {
            const singleUser = rankGroups[3][0].user;
            rank3.querySelector(".avatar-container").innerHTML = `
                <img class="top-avatar" src="${singleUser.avatar}" alt="${singleUser.name}">
            `;
            rank3.querySelector(".name").textContent = singleUser.name;
            rank3.onclick = null;
            rank3.style.cursor = 'default';
        }
    }
    
    setTimeout(() => {
        if (rank1.style.display !== 'none') rank1.classList.add('animate');
        setTimeout(() => {
            if (rank2.style.display !== 'none') rank2.classList.add('animate');
        }, 200);
        setTimeout(() => {
            if (rank3.style.display !== 'none') rank3.classList.add('animate');
        }, 400);
    }, 300);
    
    return topRankUsers;
}

// Render complete leaderboard
function renderLeaderboard(users) {
    const rankingList = document.getElementById("rankingList");
    const selfRankDiv = document.getElementById("selfRank");

    rankingList.innerHTML = "";
    selfRankDiv.innerHTML = "";

    users.sort((a, b) => b.score - a.score);

    const allRankings = calculateRankings(users);
    const topRankUsers = updateTopThree(users);
    const remainingUsers = allRankings.filter(item => item.rank > 3);
    
    let selfRank = null;
    let foundInTop3 = false;

    const selfRanking = allRankings.find(item => item.user.name === selfUsername);
    if (selfRanking && selfRanking.rank <= 3) {
        foundInTop3 = true;
    }
    
    remainingUsers.forEach((item, index) => {
        const user = item.user;
        const rank = item.rank;
        
        const li = document.createElement("li");
        li.innerHTML = `
            <span class="rank-number">${rank}</span>
            <img src="${user.avatar}" alt="${user.name}" class="avatar">
            <span class="name">${user.name}</span>
            <span class="score">${user.score}</span>
        `;
        
        li.style.animationDelay = `${index * 50}ms`;
        if (user.name === selfUsername) {
            li.classList.add('self-user');
            selfRank = { rank, ...user };
        }
        rankingList.appendChild(li);
    });

    if (selfRank) {
        selfRankDiv.innerHTML = `
            <div>
                <span class="rank-number">${selfRank.rank}</span>
                <img src="${selfRank.avatar}" alt="${selfRank.name}" class="avatar">
                <span class="name">${selfRank.name}</span>
                <span class="score">${selfRank.score}</span>
            </div>
        `;
    } else if (foundInTop3) {
        selfRankDiv.innerHTML = `
            <div>
                <span class="name">Congratulations! You're in the Top 3!</span>
            </div>
        `;
    } else {
        selfRankDiv.innerHTML = `<p>Your rank not found</p>`;
    }
}

// Run
window.addEventListener('DOMContentLoaded', () => {
    fetchLeaderboard();
});