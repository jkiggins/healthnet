function resolve_dependancy(e) {

    var oReq = new XMLHttpRequest();
    oReq.onload = reqListener;
    oReq.onerror = reqError;
    oReq.open('get', 'd', true);
    oReq.send();

}

function reqListener() {
  var data = JSON.parse(this.responseText);
  console.log(data);
}

function reqError(err) {
  console.log('Fetch Error :-S', err);
}



function set_action_and_submit(e)
{
    hfield = document.getElementById("form_action");
    hfield.value = e.dataset.action;
    e.form.submit();
}

function set_filter_and_submit(e)
{
    hfield = document.getElementById("form_filter");
    hfield.value = e.dataset.filter;
    e.form.submit();
}

function unselect_radio_set(name) {
    radios = document.getElementsByName(name);
    for(var i = 0; i < radios.length; i++)
    {
        if(radios[i].type == 'radio') {
            radios[i].checked = false;
        }
    }

}

function submit_form(e) {
    if(e.form.action[e.form.action.length-1] == 'd') {
        e.form.action = e.form.action.substr(0, e.form.action.length-1)
    }

    e.form.submit();
}

function set_kvp(key, value) {
    url_arr = window.location.pathname.split('/');

    for(var i = url_arr.length; i >= 0; i--)
    {
        if(url_arr[i] == key){
            url_arr[i+1] = value;

            window.location = rebuild_url_from_array(url_arr);
        }
    }

    url_arr.push(key);
    url_arr.push(value);

    window.location.pathname = rebuild_url_from_array(url_arr);

}

function rebuild_url_from_array(arr) {
    url = "";

    for (var i = 0; i < arr.length; i++)
    {
        if (arr[i] != "") {
            url += "/";
            url += arr[i];
        }
    }

    return url;

}