function hideAllSections() {

    let ticket = document.getElementById("ticket-details");
    let user = document.getElementById("user-info");
    let comments = document.getElementById("comments-section");
    let actions = document.getElementById("actions-section");

    if(ticket){
        ticket.style.display = "none";
    }

    if(user){
        user.style.display = "none";
    }

    if(comments){
        comments.style.display = "none";
    }

    if(actions){
        actions.style.display = "none";
    }
}

function showTicket() {

    hideAllSections();

    let ticket = document.getElementById("ticket-details");

    if(ticket){
        ticket.style.display = "block";
    }
}

function showUser() {

    hideAllSections();

    let user = document.getElementById("user-info");

    if(user){
        user.style.display = "block";
    }
}

function showComments() {

    hideAllSections();

    let comments = document.getElementById("comments-section");

    if(comments){
        comments.style.display = "block";
    }
}

function showActions() {

    hideAllSections();

    let actions = document.getElementById("actions-section");

    if(actions){
        actions.style.display = "block";
    }
}

window.onload = function(){

    if(document.getElementById("ticket-details")){
        showTicket();
    }
};

setTimeout(function() {

    const popups = document.querySelectorAll('.success-popup, .error-popup');

    popups.forEach(function(popup) {
        popup.style.opacity = '0';
        popup.style.transition = '0.5s';
    });

}, 3000);
