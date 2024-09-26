/**
 * A Javascript module to loading/refreshing options of a select2 list box using ajax based on selection of another select2 list box.
 * 
 * @url : https://gist.github.com/ajaxray/187e7c9a00666a7ffff52a8a69b8bf31
 * @auther : Anis Uddin Ahmad <anis.programmer@gmail.com>
 * 
 * Live demo - https://codepen.io/ajaxray/full/oBPbQe/
 * w: http://ajaxray.com | t: @ajaxray
 */
var Select2Cascade = ( function(window, $) {
    function Select2Cascade(parent, child, url, select2Options) {
        var afterActions = [];
        var options = select2Options || {};

        // Register functions to be called after cascading data loading done
        this.then = function(callback) {
            afterActions.push(callback);
            return this;
        };
        parent.select2(select2Options).on("change", function (e) {
            child.prop("disabled", true);
            var _this = this;
            $.getJSON(url.replace(':parentId:', $(this).val()), function(items) {
            	if(items != null){
					var newOptions = '<option></option>';
					for(var id in items) {
						for(var row in items[id]){
							newOptions += '<option value="'+ row +'">'+ items[id][row] +'</option>';
						}
					}
	                child.select2('destroy').html(newOptions).prop("disabled", false).select2(options);
            	}
                afterActions.forEach(function (callback) {
                    callback(parent, child, items);
                });
            });
        });
    }
    return Select2Cascade;
})( window, $);
