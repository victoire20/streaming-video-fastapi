$(function() {
    const BASE_URL = "http://127.0.0.1:8000";
    
    $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
        if (options.url.startsWith('/')) {
            options.url = BASE_URL + options.url;
        }
    });
});