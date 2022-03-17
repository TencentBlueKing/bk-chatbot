//以下公用代码区域，使用范围非常广，请勿更改--------------------------------
// 判断是否存在了debug的配置
if(debug_mode == "undefined"){
    var debug_mode = false;
}
//403 ajax 请求错误时artdialog提示
document.write(" <script lanague=\"javascript\" src=\""+remote_static_url+"artdialog/jquery.artDialog.js?skin=simple\"> <\/script>");


function internal_error(xhr, textStatus){
	// 用于内部异常错误处理
	var message = "系统出现异常, 请记录下错误场景并与开发人员联系, 谢谢";
	try{
		// 尝试转换为json格式的内容,然后拿到里面的message
		message = JSON.parse(xhr.responseText).message;
	}catch(err){}

	// 动态设置iframe的高度和宽度
	var ajax_content = `
		<div class="king-exception-box king-500-page pt15">
			<img src="${remote_static_url}v3/components/exception_500/images/expre_500.png">
			<h2>系统出现异常</h2>
			<p>${message}</p>
		</div> 
	`

	art.dialog({
		title: "提示",
		lock: true,
		content: ajax_content
	});
	return;
}

function access_deny(xhr){
	// 主要用于敏感权限系统的无权限或验证出错的情况
	var message = "请记录下场景和开发人员联系, 谢谢";
	try{
		// 尝试转换为json格式的内容,然后拿到里面的message
		message = JSON.parse(xhr.responseText).message;
	}catch(err){}

	// 动态设置iframe的高度和宽度
	var ajax_content = `
		<div class="king-exception-box king-403-page pt15">
			<img src="${remote_static_url}v3/components/exception_403/images/expre_403.png">
			<h2>系统权限不足</h2>
			<p>${message}</p>
		</div> 
	`

	art.dialog({
		title: "提示",
		lock: true,
		content: ajax_content
	});
	return;
}

/**
 * ajax全局设置
 */
// 在这里对ajax请求做一些统一公用处理
$.ajaxSetup({
	statusCode: {
	    403: access_deny,
	    500: internal_error,
		501: internal_error,
		503: internal_error
	}
});
/**
 * xssCheck 将用js渲染的html进行转义
 * @param str 需要转义的字符串
 * @param reg 需要转义的字符等，可选参数
*/
function xssCheck(str,reg){
    return str ? str.replace(reg || /[&<">'](?:(amp|lt|quot|gt|#39|nbsp|#\d+);)?/g, function (a, b) {
        if(b){
            return a;
        }else{
            return {
                '<':'&lt;',
                '&':'&amp;',
                '"':'&quot;',
                '>':'&gt;',
                "'":'&#39;',
            }[a]
        }
    }) : '';
}
