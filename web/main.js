var csv = function() {
    'use strict';

    var calendarEvents = [];
    var calendarStart = [
        "Subject",
        "Start Date",
        "Start Time",
        "End Date",
        "End Time",
        "All Day Event",
        "Description",
        "Location"].join(',');

    var saveData = (function () {
        var a = document.createElement("a");
        document.body.appendChild(a);
        a.style = "display: none";
        return function (data, fileName) {
            var blob = new Blob([data], {type: "octet/stream"}),
                url = window.URL.createObjectURL(blob);
            a.href = url;
            a.download = fileName;
            a.click();
            window.URL.revokeObjectURL(url);
        };
    }());

    return {
        'addEvent': function(subject, description, location, begin, stop) {
            //TODO add time and time zone? use moment to format?
            var start_date = begin;
            var end_date = stop;

            var start_year = ("0000" + (start_date.getFullYear().toString())).slice(-4);
            var start_month = ("00" + ((start_date.getMonth() + 1).toString())).slice(-2);
            var start_day = ("00" + ((start_date.getDate()).toString())).slice(-2);
            var start_hours = ("00" + (start_date.getHours().toString())).slice(-2);
            var start_minutes = ("00" + (start_date.getMinutes().toString())).slice(-2);
            var start_seconds = ("00" + (start_date.getSeconds().toString())).slice(-2);

            var end_year = ("0000" + (end_date.getFullYear().toString())).slice(-4);
            var end_month = ("00" + ((end_date.getMonth() + 1).toString())).slice(-2);
            var end_day = ("00" + ((end_date.getDate()).toString())).slice(-2);
            var end_hours = ("00" + (end_date.getHours().toString())).slice(-2);
            var end_minutes = ("00" + (end_date.getMinutes().toString())).slice(-2);
            var end_seconds = ("00" + (end_date.getSeconds().toString())).slice(-2);

            var start_time = [ start_hours, start_minutes, start_seconds ].join(':');
            var end_time = [ end_hours, end_minutes, end_seconds ].join(':');

            var calendarEvent = [
                subject,
                [ start_year, start_month, start_day].join("-"),
                start_time,
                [ end_year, end_month, end_day ].join("-"),
                end_time,
                'False',
                description,
                location
            ].join(',');
            calendarEvents.push(calendarEvent);
            return calendarEvent;
        },

        'download': function(filename, ext) {
            if (calendarEvents.length < 1) {
                return false;
            }

            var a = document.createElement("a");
            document.body.appendChild(a);
            a.style = "display: none";

            ext = (typeof ext !== 'undefined') ? ext : '.csv';
            filename = (typeof filename !== 'undefined') ? filename : 'calendar';
            var calendar = calendarStart + '\n' + calendarEvents.join('\n');
            saveData(calendar, filename + ext);
            return calendar;
        }
    };
};

function isNumeric(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

function req(url, fun, params) {
    var http = new XMLHttpRequest();
    http.open(params ? "POST" : "GET", url, true);
    // http.responseType = 'json';  // maybe some day...
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http.onreadystatechange = fun;
    http.send(params);
}

function make_player_link(player) {
    return '<a tabindex=-1 href="player.html?' + player + '">' + player + '</a>';
}

function addResults(results, scoreboard) {
    var h1 = document.createElement('h1');
    h1.innerHTML = scoreboard.shift();
    results.appendChild(h1);

    var table = document.createElement('table');
    table.id = "results";
    var tablestring = "<tr><th title=\"Namn\">Spelare<th title=\"Spelade\">S<th title=\"Vunna\">V<th title=\"Förlorade\">F<th title=\"Poäng\">P";
    for (var i=0; i<scoreboard.length; i++) {
        var score = scoreboard[i];
        tablestring += "<tr><td>" + make_player_link(score[0]) + "<td>" + score.slice(1).join("<td>");
    }
    table.innerHTML = tablestring;
    results.appendChild(table);
}

function updateResult(p1result, p2result, p1points, p2points) {
    p1result.points += p1points;
    p1result.nentries++;
    p2result.points += p2points;
    p2result.nentries++;
    if (p1points > p2points) {
        p2result.lost++;
        p1result.won++;
    } else if (p1points < p2points) {
        p1result.lost++;
        p2result.won++;
    }
}

function computeResults(round) {
    var result = {};

    if (!round.hasOwnProperty('players'))
        throw "'players' array missing";

    // Reset values
    for (var i=0; i<round.players.length; i++) {
        var player = round.players[i];
        if (result.hasOwnProperty(player))
            throw "Duplicate player name: " + player;

        result[player] = { nentries: 0, points: 0, won: 0, lost: 0 };
    }

    if (!round.hasOwnProperty('games'))
        throw "'games' array missing";

    // Score played matches into results.

    for (i=0; i<round.games.length; i++) {
        var game = round.games[i];
        if (game.length < 4)
            throw "Match med för få fält";

        var name1 = game[0],
            name2 = game[1],
            result1 = game[2],
            result2 = game[3];

        if (result[name1] === undefined)
            throw "Spelare " + name1 + " är okänd";

        if (result[name2] === undefined)
            throw "Spelare " + name2 + " är okänd";

        if (result[name1] === result[name2])
            throw "Spelare " + name1 + " kan inte spela mot sig själv";

        if (result1 == 'W') {
            updateResult(result[name1], result[name2], 4, -2);
        } else if (result2 == 'W') {
            updateResult(result[name1], result[name2], -2, 4);
        } else if (isNumeric(result1) && isNumeric(result2)) {

            if (result1 == 0 && result2 == 0)
                // For now assume match not played yet; do nothing
                continue;

            if (result1 < 0 || result1 > 3)
                throw "Resultat '" + result1 + "' är ogiltigt";
            if (result2 < 0 || result2 > 3)
                throw "Resultat '" + result2 + "' är ogiltigt";
            if (result1 + result2 > 5)
                throw "Resultat '" + result1 + "-" + result2 + "' är ogiltigt";

            // First award each player with one point for participating.
            var p1points = 1;
            var p2points = 1;

            // Give points for each won set.
            p1points += result1;
            p2points += result2;

            // Give an extra point to the winner.
            if (result1 == 3)
                p1points++;
            else if (result2 == 3)
                p2points++;
            updateResult(result[name1], result[name2], p1points, p2points);
        }
    }

    // Now convert results into a sorted list of results.

    var arr = [];

    for (var name in result)
        arr.push([name, result[name].nentries, result[name].won, result[name].lost, result[name].points]);

    arr.sort(function(a, b) {
        var points1 = a[4];
        var points2 = b[4];
        if (points1 == points2) {
            for (var i=0; i<round.games.length; i++) {
                var game = round.games[i];
                var name1 = game[0],
                    name2 = game[1],
                    result1 = game[2],
                    result2 = game[3];

                if ((name1 == a[0] && name2 == b[0]) ||
                    (name1 == b[0] && name2 == a[0]))
                    return result2 - result1;
            }
            // No played match between them. What to do? FIXME: Count games.
            return Math.random() - 0.5;
        } else {
            return points2 - points1;
        }
    });

    var namearr = parse_division_name(division_name);
    if (namearr)
        arr.unshift("Division " + parseInt(namearr[2]) + " <br>Omgång " + parseInt(namearr[1]) +
                    " &bull; " + namearr[0].replace("-", "/"));

    return arr;
}

var yearselect = document.querySelector('#yearselection');
var roundselect = document.querySelector('#roundselection');
var divisionselect = document.querySelector('#divisionselection');
var errorblock = document.querySelector('#error');

var results = document.querySelector('#results');
var division_name;
var admin = document.location.hash.substr(1).split('/')[1] == 'admin';
if (admin)
    document.querySelector('.admin').style.display = 'block';

var currenthash = ""; // current object we're working on
var round = {};

function save(tr) {
    if (!division_name)
        return;
    tr.querySelector("td:last-child").textContent = '';
    req("save.cgi",
        function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                if (response && response.length > 0) {
                    currenthash = response[0];
                    tr.querySelector("td:last-child").textContent = '✔';
                } else {
                    tr.querySelector("td:last-child").textContent = '!';
                    errorblock.innerHTML = "Kunde inte spara!";
                }
            }
        }, "division=" + encodeURIComponent(division_name) + "&parent=" +
           encodeURIComponent(currenthash) + "&data=" + encodeURIComponent(JSON.stringify(round)));
}

function build_scoreboard() {
    results.innerHTML = '';
    errorblock.innerHTML = '';

    try {
        addResults(results, computeResults(round));
    } catch (e) {
        errorblock.innerHTML = e;
        throw (e);
    }
}

function on_round_changed() {
    errorblock.innerHTML = "";

    if (round == {}) {
        errorblock.innerHTML = '<i>Empty round</i>';
        return;
    }

    build_ui_area();
    build_scoreboard();
}

function option(value, selected) {
    var x = document.createElement('option');
    x.text = value;
    if (value == selected)
        x.selected = true;
    return x;
}

function parse_division_name(division_name) {
    var re = /(\d\d\d\d-\d\d\d\d)-(\d\d)-(\d\d)/;
    var found = division_name.match(re);
    if (found)
        return found.slice(1,4);
    else
        return null;
}

var years = {};

function update_list() {
    var requested_year = division_name ? parse_division_name(division_name)[0] : 0;
    req("list.cgi",
        function() {
            if (this.readyState == 4 && this.status == 200) {
                years = {};

                var response = JSON.parse(this.responseText);

                for (var i=0; i<response.length; i++) {
                    var res = parse_division_name(response[i]);
                    if (res) {
                        if (!years[res[0]])
                            years[res[0]] = { };
                        if (!years[res[0]][res[1]])
                            years[res[0]][res[1]] = [];
                        years[res[0]][res[1]].push(res[2]);
                    }
                }

                for (i=0; i<Object.keys(years).length; i++) {
                    var year = Object.keys(years)[i];
                    yearselect.add(option(year, requested_year));
                }

                if (!division_name)
                    yearselect.options[yearselect.options.length - 1].selected = true;

                update_roundnr();

                if (admin) {
                    var resultsroot = document.querySelector('.admin .results');
                    resultsroot.innerHTML = 'Hämta resultat: ';

                    var select = document.createElement('select');
                    var opt = document.createElement('option');
                    opt.textContent = '---';
                    opt.value = '---';
                    select.add(opt);

                    for (i=0; i<Object.keys(years).length; i++) {
                        var season = Object.keys(years)[i];
                        for (var j=0; j<Object.keys(years[season]).length; j++) {
                            var round = Object.keys(years[season])[j];
                            opt = document.createElement('option');
                            opt.textContent = season + " | " + round;
                            opt.value = season + "," + round;
                            select.add(opt);
                        }
                    }
                    select.onchange = function() {
                        if (this.value == '---')
                            return;
                        var arr = this.value.split(',');

                        var xhr = new XMLHttpRequest();
                        xhr.open('POST', 'results.cgi');
                        xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
                        xhr.onload = function () {
                            var a = document.createElement("a");
                            resultsroot.appendChild(a);
                            a.style = "display: none";
                            var res = this.responseText;
                            var blob = new Blob([res], {type: "text/csv"}),
                                url = window.URL.createObjectURL(blob);
                            a.href = url;
                            a.download = "Squash_league_results-" + arr[0] + "-" + arr[1] + ".csv";
                            a.click();
                            window.URL.revokeObjectURL(url);
                        };
                        xhr.send('format=chris&season=' + arr[0] + '&round=' + arr[1]);
                    }
                    resultsroot.appendChild(select);
                }

            }
        });
}

function update_roundnr(event) {
    var requested_roundnr = division_name ? parse_division_name(division_name)[1] : 0;
    roundselect.innerHTML = '';
    for (var i=0; i<Object.keys(years[yearselect.value]).length; i++) {
        var round = Object.keys(years[yearselect.value])[i];
        roundselect.add(option(round, requested_roundnr));
    }
    if (!division_name)
        roundselect.options[roundselect.options.length - 1].selected = true;
    update_divisionnr(event);
}

function update_divisionnr(event) {
    var requested_divisionnr = division_name ? parse_division_name(division_name)[2] : 0;
    divisionselect.innerHTML = '';
    var array = years[yearselect.value][roundselect.value].sort(function(a,b){return a - b});
    for (var i=0; i<array.length; i++) {
        var divisionnr = array[i];
        divisionselect.add(option(divisionnr, requested_divisionnr));
    }
    update_round(event);
}

function update_round(event) {
    if (event || !division_name) {
        division_name = yearselect.value + "-" + roundselect.value + "-" + divisionselect.value;
        document.location.hash = division_name;

        load_round();
    }
}

function load_round() {
    req("load.cgi?division=" + division_name,
        function() {
            if (this.readyState == 4 && this.status == 200) {
                try {
                    var response = JSON.parse(this.responseText);
                    round = response[4];
                    if (admin)
                        document.querySelector('.editui textarea').value = JSON.stringify(round);
                    currenthash = response[0];
                    on_round_changed();
                } catch (e) {
                    errorblock.innerHTML = e;
                    throw(e);
                }
            }
        });
}

function setup_raw_edit() {
    var toggle = document.querySelector('.edit a');
    toggle.onclick = function(event) {
        document.querySelector('.editui').style.display = 'block';
        event.preventDefault();
    }

    document.querySelector('.editui input[type=submit]').onclick = function() {
        var data = document.querySelector('.editui textarea').value;
        req("save.cgi",
            function() {
                if (this.readyState == 4 && this.status == 200) {
                    var response = JSON.parse(this.responseText);
                    if (response) {
                        currenthash = response[0];
                        load_round();
                    }
                    else
                        errorblock.innerHTML = "Kunde inte spara!";
                }
            }, "division=" + encodeURIComponent(division_name) + "&parent=" +
               encodeURIComponent(currenthash) + "&data=" + encodeURIComponent(data));
    }
}

function update_division_name_from_hash() {
    division_name = document.location.hash.substr(1).split('/')[0];
    if (division_name)
        load_round();
}

function build_select(classname) {
    return '<select class=' + classname +
           '><option>-<option>0<option>1<option>2<option>3<option>W</select>';
}

function make_onchange_func(colidx, othercolidx) {
    return function() {
        var tr = this.parentNode.parentNode;
        var gameidx = tr.getAttribute("data-game-idx");
        if (this.value == 'W')
            round.games[gameidx][colidx] = 'W';
        else if (this.value == '-')
            round.games[gameidx][colidx] = '-';
        else {
            round.games[gameidx][colidx] = parseInt(this.value);
            if (isNaN(round.games[gameidx][colidx]))
                this.value = round.games[gameidx][colidx] = '-';
        }

        if (round.games[gameidx][colidx] != '-' &&
            round.games[gameidx][othercolidx] != '-') {
            build_scoreboard();
            save(tr);
        }
    }
}

function build_ui_area() {
    var uiarea = document.querySelector('.uiarea');
    uiarea.innerHTML = '';

    var table = document.createElement('table');

    round.games.forEach(function(game, i) {
        if (i % 3 == 0) {
            var tr = document.createElement('tr');
            var header = (game[4] || "");
            tr.innerHTML = '<th colspan=7><h2>' + header + '</h2>';
            table.appendChild(tr);
        }

        tr = document.createElement('tr');
        tr.setAttribute("data-game-idx", i);

        tr.innerHTML = '<td>' + make_player_link(game[0]) +
                       '<td>' + make_player_link(game[1]) +
                       '<td>Bana ' + (game[6] || "?") +
                       '<td>' + (game[5] || "") +
                       '<td>' + build_select('p1') +
                       '<td>' + build_select('p2') +
                       '<td>'; // last col for save check mark.

        tr.querySelector('select.p1').value = game[2];
        tr.querySelector('select.p2').value = game[3];

        tr.querySelector('select.p1').onchange = make_onchange_func(2, 3);
        tr.querySelector('select.p2').onchange = make_onchange_func(3, 2);

        table.appendChild(tr);
    });
    uiarea.appendChild(table);

    var div = document.createElement('div');
    div.className = "downloadcsv";
    div.textContent = "Ladda ner .csv-fil: ";
    var select = document.createElement('select');
    var option = document.createElement('option');
    option.textContent = "---";
    select.appendChild(option);
    round.players.forEach(function(player) {
        var option = document.createElement('option');
        option.textContent = player;
        select.appendChild(option);
    });

    select.onchange = function (event) {
        var player = event.target.value;
        if (player == "---")
            return;
        var cal = csv();
        round.games.forEach(function(game) {
            if (game[0] == player || game[1] == player) {
                var date = game[4].replace("-", "/");
                var begin = new Date(date + " " + game[5] + ":00");
                var end = new Date(begin.getTime());
                end.setMinutes(begin.getMinutes() + 45);
                cal.addEvent(game[0] + ' - ' + game[1],
                             game[0] + ' - ' + game[1] + ' på bana ' + game[6],
                             'Landala Squashhall', begin, end);
            }
        });
        cal.download(division_name + "_" + player.replace(/[^a-z0-9]/gi, '_').toLowerCase());
    };

    div.appendChild(select);
    uiarea.appendChild(div);
}

yearselect.onchange = update_roundnr;
roundselect.onchange = update_divisionnr;
divisionselect.onchange = update_round;
window.onhashchange = update_division_name_from_hash;

update_division_name_from_hash();
update_list();
setup_raw_edit();
