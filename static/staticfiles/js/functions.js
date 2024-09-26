function _jsonContains(json, value) {
    let contains = false;
    Object.keys(json).some(key => {
        contains = typeof json[key] === 'object' ? _isContains(json[key], value) : json[key] === value;
        return contains;
    });
    return contains;
 }

 function printObject() {
    window.print();
}

$('#floatprint').on('click', function(){
    window.setTimeout(function() { printObject(); }, 0);
});

$(document).on('keydown', function(e) {
    if(e.ctrlKey && (e.key == "p" || e.charCode == 16 || e.charCode == 112 || e.keyCode == 80) ){
        Swal.fire("Print Warning",
        "Please use the PRINT button on the upper left part of the page for better rendering of the document in the print dialog.",
        "warning");
        e.cancelBubble = true;
        e.preventDefault();
        e.stopImmediatePropagation();
    }
});

//$('.icheck').iCheck({
//    checkboxClass: 'icheckbox_square-green',
//    radioClass: 'iradio_square-green',
//});

function changeURLhistory(window, statedata, title, newURL){
    if (window.history.replaceState) {
       window.history.replaceState(statedata, title, newURL);
    }
}
