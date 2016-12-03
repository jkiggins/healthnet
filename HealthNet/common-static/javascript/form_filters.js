// Create and update event
String.prototype.format_py = function () {
	var str = this;
	for(var i = 0; i < arguments.length; i++)
	{
		str = str.replace("{"+(i-1).toString()+"}", arguments[i]);
	}

	return str;
};

function resolve_pd_dependancy(e) {

    var oReq = new XMLHttpRequest();
    oReq.onload = reqListener;
    oReq.onerror = reqError;
    oReq.open('POST', 'd', true);

    //oReq.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));

    oReq.send(new FormData(e.form));
}

function reqListener() {
    var html = this.responseText;
	if (html.toUpperCase() != "PASS") {
		document.getElementById('create_event_form').innerHTML = html;
		initForms();
	}
}

function reqError(err) {
  console.log('Fetch Error :-S', err);
}

//EMR
function ajax_emr_item(e) {

    var oReq = new XMLHttpRequest();
    oReq.onload = emr_reqListener;
    oReq.onerror = reqError;
    oReq.open('POST', 'v', true);
	var csrftoken = Cookies.get('csrftoken');
	oReq.setRequestHeader("X-CSRFToken", csrftoken);

    oReq.send(JSON.stringify({'emrpk': e.dataset.pk}));
	return false;
}

function emr_reqListener() {
    var html = this.responseText;
	if (html.toUpperCase() != "PASS") {
		var overlay = document.getElementById('vemr_overlay');
		overlay.innerHTML = html;
		overlay.setAttribute("class", "overlay");
		document.body.setAttribute("class", "noscroll");

		$(function(){$(".emr_test_image_wrap").resizable({aspectRatio: true});});
	}
}

function newTab(url) {
	var win = window.open(url, '_blank');
  win.focus();

}

function emr_action_ajax(e, action) {
	var oReq = new XMLHttpRequest();
    oReq.onload = emr_reqListener;
    oReq.onerror = reqError;
    oReq.open('POST', 'a', true);
	var csrftoken = Cookies.get('csrftoken');
	oReq.setRequestHeader("X-CSRFToken", csrftoken);


    oReq.send(JSON.stringify({'emrpk': e.dataset.pk,'action': action}));
	return false;
}

function overlay_off(e) {
	e.setAttribute("class", "hidden");
	document.body.setAttribute("class", "");

}

function ajax_dismiss_note(e){
	var oReq = new XMLHttpRequest();
    oReq.onerror = reqError;
    oReq.open('POST', e.dataset.dis_url, true);
	var csrftoken = Cookies.get('csrftoken');
	oReq.setRequestHeader("X-CSRFToken", csrftoken);

    oReq.send()
    e.remove()
}


function stop_event_prop(e)
{
	e.stopPropagation();
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

function submit_on_enter(e) {
	if (e.keyCode == keys.ENTER)
	{
		e.submit()
	}
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

function postJson(url, json) {
	var form = document.getElementById("hiddenformpost");

	if (form !== null) {
		form.children[1].setAttribute("value", JSON.stringify(json));
		form.setAttribute("action", url);
		console.log(form.innerHTML);
		form.submit();
	}
}

function go(url) {
	window.location=url;

}

function initBody() {
	doTooltip();
	initForms();
	noteDropdown();
}

function noteDropdown() {
	document.getElementById("note").onclick = function (e) {
		var drop = document.getElementById(e.target.id+"_drop")
		if (drop.className.indexOf("hide") == -1)
		{
			drop.className = drop.className.replace("show", "hide")
		}else{
			drop.className = drop.className.replace("hide", "show")
		}
	}

}

function doTooltip() {

	$( function() {
    $( document ).tooltip();
  } );

}

function initForms() {
	initPickers(['dateTimeId_1']);
}

function initPickers(ids) {
	for(var i = 0; i < ids.length; i++)
	{
		var ele = document.getElementById(ids[i]);
		if (ele !== null) {
			initTimePicker(ele);
		}
	}

	$('.clockpicker').clockpicker({
		placement: 'bottom',
		align: 'left',
		donetext: 'Done',
		twelvehour: true
	});

}

function initTimePicker(ele) {
	var html = "<div class='input-group clockpicker'> \
    <span class='input-group-addon'> \
        <span class='glyphicon glyphicon-time'></span> \
    </span> \
</div>";


	var clock = document.implementation.createHTMLDocument("clock")
	clock.documentElement.innerHTML = html;
	ele.className += " form-control";
	clock.body.childNodes[0].insertBefore(ele.cloneNode(), clock.body.childNodes[0].childNodes[0]);

	console.log(clock.body.innerHTML);

	ele.parentElement.replaceChild(clock.body.childNodes[0], ele);
}

/*!
 * JavaScript Cookie v2.1.3
 * https://github.com/js-cookie/js-cookie
 *
 * Copyright 2006, 2015 Klaus Hartl & Fagner Brack
 * Released under the MIT license
 */
;(function (factory) {
	var registeredInModuleLoader = false;
	if (typeof define === 'function' && define.amd) {
		define(factory);
		registeredInModuleLoader = true;
	}
	if (typeof exports === 'object') {
		module.exports = factory();
		registeredInModuleLoader = true;
	}
	if (!registeredInModuleLoader) {
		var OldCookies = window.Cookies;
		var api = window.Cookies = factory();
		api.noConflict = function () {
			window.Cookies = OldCookies;
			return api;
		};
	}
}(function () {
	function extend () {
		var i = 0;
		var result = {};
		for (; i < arguments.length; i++) {
			var attributes = arguments[ i ];
			for (var key in attributes) {
				result[key] = attributes[key];
			}
		}
		return result;
	}

	function init (converter) {
		function api (key, value, attributes) {
			var result;
			if (typeof document === 'undefined') {
				return;
			}

			// Write

			if (arguments.length > 1) {
				attributes = extend({
					path: '/'
				}, api.defaults, attributes);

				if (typeof attributes.expires === 'number') {
					var expires = new Date();
					expires.setMilliseconds(expires.getMilliseconds() + attributes.expires * 864e+5);
					attributes.expires = expires;
				}

				try {
					result = JSON.stringify(value);
					if (/^[\{\[]/.test(result)) {
						value = result;
					}
				} catch (e) {}

				if (!converter.write) {
					value = encodeURIComponent(String(value))
						.replace(/%(23|24|26|2B|3A|3C|3E|3D|2F|3F|40|5B|5D|5E|60|7B|7D|7C)/g, decodeURIComponent);
				} else {
					value = converter.write(value, key);
				}

				key = encodeURIComponent(String(key));
				key = key.replace(/%(23|24|26|2B|5E|60|7C)/g, decodeURIComponent);
				key = key.replace(/[\(\)]/g, escape);

				return (document.cookie = [
					key, '=', value,
					attributes.expires ? '; expires=' + attributes.expires.toUTCString() : '', // use expires attribute, max-age is not supported by IE
					attributes.path ? '; path=' + attributes.path : '',
					attributes.domain ? '; domain=' + attributes.domain : '',
					attributes.secure ? '; secure' : ''
				].join(''));
			}

			// Read

			if (!key) {
				result = {};
			}

			// To prevent the for loop in the first place assign an empty array
			// in case there are no cookies at all. Also prevents odd result when
			// calling "get()"
			var cookies = document.cookie ? document.cookie.split('; ') : [];
			var rdecode = /(%[0-9A-Z]{2})+/g;
			var i = 0;

			for (; i < cookies.length; i++) {
				var parts = cookies[i].split('=');
				var cookie = parts.slice(1).join('=');

				if (cookie.charAt(0) === '"') {
					cookie = cookie.slice(1, -1);
				}

				try {
					var name = parts[0].replace(rdecode, decodeURIComponent);
					cookie = converter.read ?
						converter.read(cookie, name) : converter(cookie, name) ||
						cookie.replace(rdecode, decodeURIComponent);

					if (this.json) {
						try {
							cookie = JSON.parse(cookie);
						} catch (e) {}
					}

					if (key === name) {
						result = cookie;
						break;
					}

					if (!key) {
						result[name] = cookie;
					}
				} catch (e) {}
			}

			return result;
		}

		api.set = api;
		api.get = function (key) {
			return api.call(api, key);
		};
		api.getJSON = function () {
			return api.apply({
				json: true
			}, [].slice.call(arguments));
		};
		api.defaults = {};

		api.remove = function (key, attributes) {
			api(key, '', extend(attributes, {
				expires: -1
			}));
		};

		api.withConverter = init;

		return api;
	}

	return init(function () {});
}));