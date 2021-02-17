package main

import (
	"github.com/didip/tollbooth"
	"github.com/didip/tollbooth/limiter"
	"html/template"
	"io"
	"log"
	"net/http"
	"net/url"
	"strings"
	"time"
)

var indexPage []byte

func index(w http.ResponseWriter, _ *http.Request) {
	_, _ = w.Write(indexPage)
}

func theme(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")

	themeUrl, err := url.Parse("https://raw.githubusercontent.com/1337-themes/themes/main/" + name + ".html")
	if err != nil {
		http.Error(w, "could not parse themeUrl", http.StatusBadRequest)
		return
	}
	themeUrl = themeUrl.ResolveReference(themeUrl)

	if !strings.HasPrefix(themeUrl.String(), "https://raw.githubusercontent.com/1337-themes/themes/") {
		http.Error(w, "invalid themeUrl", http.StatusBadRequest)
		return
	}

	resp, err := http.Get(themeUrl.String())
	if err != nil {
		http.Error(w, "could not connect to github, contact Larry on Slack.", http.StatusInternalServerError)
		return
	}

	reader := http.MaxBytesReader(nil, resp.Body, 10000)

	buf := new(strings.Builder)
	_, err = io.Copy(buf, reader)
	if err != nil {
		http.Error(w, "failed to get template", http.StatusBadRequest)
		return
	}

	themeTemplate := template.New(name)
	themeTemplate, err = themeTemplate.Parse(buf.String())
	if err != nil {
		http.Error(w, "invalid template", http.StatusBadRequest)
		return
	}

	err = themeTemplate.Execute(w, map[string]string{
		"Flag": "ctf{00000000000000000000000000000000}",
		"Title": "Hello, World!",
		"Message": "How does this template look?",
	})

	if err != nil {
		http.Error(w, "failed to execute template", http.StatusBadRequest)
	}
}

func main() {
	indexPage = []byte(`<!DOCTYPE html>
<html>
<head>
	<title>Themes</title>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<style>
		* {
			font-family: sans-serif;
			font-size: 1em;
		}
		.flex-center {
			display: flex;
			align-items: center;
			justify-content: center;
			flex-direction: column;
		}
		body {
			margin: 0;
			height: 100vh;
			background-color: #FAEBD7;
		}
		#form {
			width: 90vw;
			max-width: 300px;
			height: 90vh;
			max-height: 50px;
			flex-direction: row;
			background-color: white;
			border-radius: 15px;
		}
		#theme {
			width: 90vw;
			height: 90vh;
			max-width: 600px;
			max-height: 300px;
		}
		#theme-container {
			background-color: white;
			border-radius: 15px;
			padding: 15px;
		}
		button {
			margin-left: 5px;
		}
	</style>
</head>
<body class="flex-center">
	<form id="form" class="flex-center" action="javascript:window.displayTheme()" method="POST">
		<input name="theme" id="theme-input" placeholder="Theme Name"> <button type="submit">Display!</button>
	</form>
	<br>
	<div id="theme-container" hidden>
		<iframe id="theme"></iframe>
	</div>
</body>
<script>
window.displayTheme = () => {
	document.getElementById('theme-container').hidden = false;
	document.getElementById('theme').src = '/theme?name=' + encodeURIComponent(document.getElementById('theme-input').value)
}
</script>
</html>`)

	// request limit: 1 per 4 seconds
	// pls don't spam so i don't get banned from github ;-;
	requestLimiter := tollbooth.NewLimiter(0.25, &limiter.ExpirableOptions{
		DefaultExpirationTTL: 5 * time.Minute,
	})
	requestLimiter.SetIPLookups([]string{"RemoteAddr"})

	http.HandleFunc("/", index)
	http.Handle("/theme", tollbooth.LimitFuncHandler(requestLimiter, theme))

	log.Fatal(http.ListenAndServe(":5004", nil))
}