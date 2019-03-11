$(function () {
    var conn = null;
    var name = "UNKNOWN";
    var logs = [];
    var MAX = 10;

    function log(msg, name) {
        var control = $('#log');
        var date = new Date();
        var date_prompt = date.toISOString().split('T')[1].slice(0, 8);
        if (typeof name === 'undefined') {
            name = '';
        }
        name = '<span class="name">' + name + '</span>';
        msg = '<span class="message">' + msg + '</span>';
        date_prompt = '<span class="date">' + date_prompt + '</span>';

        var allText = '<div class="line">' + date_prompt + name + msg + '</div>';
        logs.unshift(allText);
        var logsToRender = logs.slice(0, MAX);
        logs = logs.slice(0, MAX);
        logsToRender.reverse();

        control.html(logsToRender.join(''));
        control.scrollTop(control.scrollTop() + 1000);
    }

    function connect() {
        disconnect();
        var wsUri = (window.location.protocol == 'https:' && 'wss://' || 'ws://') + window.location.host;
        conn = new WebSocket(wsUri);
        conn.onopen = function () {
            update_ui();
        };
        conn.onmessage = function (e) {
            var data = JSON.parse(e.data);
            switch (data.action) {
                case  'connect':
                    name = data.name;
                    break;
                case  'disconnect':
                    break;
                case 'join':
                    break;
                case 'sent':
                    log(data.text, data.name);
                    break;
            }
        };
        conn.onclose = function () {
            log('>> Disconnected.');
            conn = null;
            update_ui();
        };
    }

    function disconnect() {
        if (conn != null) {
            conn.close();
            conn = null;
            name = 'UNKNOWN';
            update_ui();
        }
    }

    var timestampInterval = setInterval(function () {
        var now = +new Date();
        now = Math.floor(now / 1000);
        now = now + 60;

        $('.ts').text(now);
    }, 1000)


    window.addEventListener("beforeunload", function (event) {
        disconnect();
        clearInterval(timestampInterval);
    });
    var emojis = ["🤩", "🤪", "🤭", "🤫", "🤨", "🤮", "🤯", "🧐", "🤬", "🧡", "🤟", "🤲", "🧠", "🧒", "🧑", "🧔", "🧓", "🧕", "🤱", "🧙", "🧚", "🧛", "🧜", "🧝", "🧞", "🧟", "🧖", "🧗", "🧘", "🦓", "🦒", "🦔", "🦕", "🦖", "🦗", "🥥", "🥦", "🥨", "🥩", "🥪", "🥣", "🥫", "🥟", "🥠", "🥡", "🥧", "🥤", "🥢", "🛸", "🛷", "🥌", "🧣", "🧤", "🧥", "🧦", "🧢",];

    function update_ui() {
        $('.proto').text(window.location.protocol);
        $('.host').text(window.location.host);
        var randomPayload = emojis[Math.floor(Math.random() * emojis.length)];
        $('.payload').text(randomPayload);
        $('#copycurl').prop("disabled", false);
    }

    $('#copycurl').on('click', function () {
        var cmd = $('#curlcommand')[0].innerText;
        copyToClipboard(cmd);
        return false;
    });

    function copyToClipboard(str) {
        const el = document.createElement('textarea');
        el.value = str;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
    };

    connect();
});