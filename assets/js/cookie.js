
function setCookie(name, value, hours) {
    const expires = new Date();
    expires.setTime(expires.getTime() + hours * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
}



function getCookie(name) {
    let cookieValue = '';
    let cookieExpiry = '';

    const cookieName = `${name}=`;
    const cookieArray = document.cookie.split(';');
    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();

        if (cookie.indexOf(cookieName) === 0) cookieValue = cookie.substring(cookieName.length, cookie.length);
        if (cookie.indexOf('expires=') === 0) cookieExpiry = cookie.substring('expires='.length, cookie.length);

        if(cookieValue && cookieExpiry) break;
    }
    
    if (cookieExpiry) {

        const expirationDate = new Date(cookieExpiry);
        if( expirationDate < new Date() ) cookieValue = ''; // expired

    }

    return cookieValue;
}


function deleteCookie(name) {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1990 00:00:00 UTC;path=/;`;
}