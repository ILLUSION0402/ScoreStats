//Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');
if (mobileMenuButton && mobileMenu){
    mobileMenuButton.addEventListener('click', function() {
        mobileMenu.classList.toggle('hidden');
    });
}
});

function formatNumber(num){
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
function formatOvers(overs){
    const value = Number(overs);
    if (Number.isNaN(value)) return "0.0 overs";
    return value.toFixed(1)+" overs";
}
function timeAgo(date){
    const parsed = date instanceof Date ? date : new Date(date);
    if (Number.isNaN(parsed.getTime())) return "just now";
    const seconds=Math.floor((new Date()-parsed)/1000);
    let interval=seconds/31536000;
    if (interval>1){
        return Math.floor(interval)+" years ago";
    }
    interval=seconds/2592000;
    if (interval>1){
        return Math.floor(interval)+" months ago";
    }
    interval=seconds/86400;
    if (interval>1){
        return Math.floor(interval)+" days ago";
    }
    interval=seconds/3600;
    if (interval>1){
        return Math.floor(interval)+" hours ago";
    }
    interval=seconds/60;
    if (interval>1){
        return Math.floor(interval)+" minutes ago";
    }
    return Math.floor(seconds)+" seconds ago";
}

//show toast notifications
function showToast(message, type="info"){
    const toast=document.createElement('div');
    toast.className=`fixed top-4 right-4 px-6 py-4 rounded shadow-lg text-white ${type==="success"?"bg-green-500":type==="error"?"bg-red-500":"bg-blue-500"} fade-in`;
    toast.textContent=message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
function copyToClipboard(text){
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showToast("Link copied to clipboard!", "success");
        }).catch(() => {
            showToast("Failed to copy link.", "error");
        });
        return;
    }

    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-9999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        const ok = document.execCommand("copy");
        showToast(ok ? "Link copied to clipboard!" : "Failed to copy link.", ok ? "success" : "error");
    } catch (_) {
        showToast("Failed to copy link.", "error");
    } finally {
        document.body.removeChild(textArea);
    }
}
window.cricketUtils={
    formatNumber,
    formatOvers,
    timeAgo,
    showToast,
    copyToClipboard
};
