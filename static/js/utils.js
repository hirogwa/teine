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

module.exports = {
    formatDate: formatDate,
    formatDatetime: formatDatetime
};
