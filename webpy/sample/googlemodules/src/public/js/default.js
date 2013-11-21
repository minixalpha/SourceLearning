var g_shown = false;

function showLivePreview(url)
{
    hideElm("screenshot");
    showElm("livePreview");
    if (!g_shown || true) {
        g_shown = true;
        var iframe = document.getElementById("previewFrame");
        iframe.src = url;
    }
}

function hideLivePreview()
{
    hideElm("livePreview");
    showElm("screenshot");
}

function toggleElm(name)
{
    var elm = document.getElementById(name);
    elm.style.display = (elm.style.display == "block") ? "none" : "block";
}

function showElm(name)
{
    var elm = document.getElementById(name);
    elm.style.display = "block";
}

function hideElm(name)
{
    var elm = document.getElementById(name);
    elm.style.display = "none";
}
