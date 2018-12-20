odoo.define('suvit_support.Support', function(require){

var UserMenu = require('web.UserMenu');

UserMenu.include({
  on_menu_support: function(){
    window.open('https://suvit.ru', '_blank');
  }
});

});
