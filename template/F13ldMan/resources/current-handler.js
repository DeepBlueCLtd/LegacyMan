/* this function appends a `current` class to a link in the
header menu if it is for the current page */
document.onreadystatechange = function () {
    if (document.readyState === 'complete') {
        const curPage = document.URL;
        const links = document.getElementsByTagName('a');
        for (let link of links) {
            if (link.href == curPage) {
                link.classList.add("current");
            }
        }
    }
};