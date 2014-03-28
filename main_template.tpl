<head>
<meta http-equiv="refresh" content="5">
</head>
<body>
<h1>Fishtank</h1>
The current pwm level is {{current_level}}, dim time is {{dim_time}}
%if modding:
    <p>Currently dimming</p>
%else:
    <p>Not dimming at the moment</p>
%end

<form action="dim_on" method="put">
<button>Dim on</button>
</form>
<form action="dim_off" method="put">
<button>Dim off</button>
</form>
<form action="turn_on" method="put">
<button>Turn on</button>
</form>
<form action="turn_off" method="put">
<button>Turn off</button>
</form>

<form action="set_dim" method="post">
Dim Time(secs): <input type="text" name="dim_time">
<button>Set</button>
</form>

</body>
