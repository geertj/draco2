<%@ include file="/header.inc" %>

<h1>Form AJAX testing</h1>

<p> Vul maar iets in ... </p>

<p id="user_message"></p>

<form id="user">
<table>
<tr>
  <td id="user_name_label">Name</td>
  <td><input type="text" name="name" /></td>
</tr>
<tr>
  <td id="user_surname_label">Surname</td>
  <td><input type="text" name="surname" /></td>
</tr>
</table>
</form>

<script type="text/javascript" src="/support/files/compat.js"></script>
<script type="text/javascript" src="/support/files/ajax.js"></script>
<script type="text/javascript" src="/support/files/webui.js"></script>
<script type="text/javascript" src="/support/files/form.js"></script>

<script type="text/javascript">
var fields = new Array("name", "surname");
var user_form = new Form("user", "/test/submit.dsp", fields);
</script>

<p> <a href="javascript:user_form.submit()">Submit the Form (without POST!)</a> </p>

<%@ include file="/footer.inc" %>
