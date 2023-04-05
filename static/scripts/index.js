(function () {
    const baseurl = window.location.href.replace(/\/$/, "") + "/api";
    async function fetchAPI(path, method = "GET", data) {
        url = baseurl + path;
        body = data && JSON.stringify(data);
        ret = await fetch(url, { body, method });
        return await ret.json();
    }
    window.BINJHub = window.BINJHub || {};
    window.BINJHub.getUser = async function () {
        return await fetchAPI("/me");
    };
})();