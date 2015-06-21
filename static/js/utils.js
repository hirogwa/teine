var formatTwoDigits = function(n) {
    return n < 10 ? '0{}'.replace('{}', n) : n;
};

var formatDate = function(date) {
    return 'yyyy-MM-dd'
        .replace('yyyy', date.getFullYear())
        .replace('MM', formatTwoDigits(date.getMonth() + 1))
        .replace('dd', formatTwoDigits(date.getDate()));
};

var formatDatetime = function(date) {
    return 'yyyy-MM-dd hh:mm'
        .replace('yyyy', date.getFullYear())
        .replace('MM', formatTwoDigits(date.getMonth() + 1))
        .replace('dd', formatTwoDigits(date.getDate()))
        .replace('hh', formatTwoDigits(date.getHours()))
        .replace('mm', formatTwoDigits(date.getMinutes()));
};

var getUrls = function(url) {
    var ssl = '';
    var nonssl = '';
    if (url.startsWith('http://')) {
        nonssl = url;
    } else if (url.startsWith('https://')) {
        ssl = url;
    } else {
        ssl = 'https://{}'.replace('{}', url);
        nonssl = 'http://{}'.replace('{}', url);
    }
    return {
        ssl: ssl,
        nonssl: nonssl,
        raw: url
    };
};

var toHttpUrl = function(url) {
    if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
    } else {
        return 'http://{}'.replace('{}', url);
    }
};

var uploadData = function(url, data) {
        return new Promise(function(resolve, reject) {
            $.ajax({
                url: url,
                data: data,
                cache: false,
                processData: false,
                contentType: false,
                method: 'POST',
                success: function(data) {
                    console.log(data);
                    resolve(data);
                },
                error: function(data) {
                    console.log(data);
                    reject(data);
                }
            });
        });
};

module.exports = {
    formatDate: formatDate,
    formatDatetime: formatDatetime,
    getUrls: getUrls,
    toHttpUrl: toHttpUrl,
    uploadData: uploadData
};
