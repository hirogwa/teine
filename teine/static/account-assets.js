teineAccount = {};
$(function() {
    require('./css/user_account.css');
    require('./js/esnext.js');

    teineAccount.UserSignupView =
        require('./js/views/account/user-signup.js').UserSignupView;
});
