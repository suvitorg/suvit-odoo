odoo.define('suvit_support.Support', function(require){
  var UserMenu = require('web.UserMenu')
  var Custom_Menu = UserMenu.include({
    on_menu_support: function(){      
      window.open('https://suvit.ru', '_blank')
    }
  })
return Custom_Menu
})
