(function () {
    const baseurl = window.location.pathname.replace(/\/$/, "") + "/api";
    async function fetchAPI(path, method = "GET", data) {
        url = baseurl + path;
        body = data && JSON.stringify(data);
        headers = data && { "Content-Type": "application/json" };
        ret = await fetch(url, { body, method, headers });
        return await ret.json();
    }
    window.BINJHub = window.BINJHub || {};
    window.BINJHub.getUser = async function () {
        return await fetchAPI("/me");
    };
})();