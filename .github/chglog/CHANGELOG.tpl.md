# {{ .Info.Title }}  

{{- if .Unreleased.Commits -}}
<a name="unreleased"></a>

{{ range .Unreleased.Commits }}
* {{ .Subject }} `{{ .Author.Name }} at {{ .Author.Date.Format "2006-01-02 15:04:05 UTC" }}`
{{ end }}
{{ end }}

{{ range .Versions }}
<a name="{{ .Tag.Name }}"></a>
## {{ if .Tag.Previous }}[{{ .Tag.Name }}]({{ $.Info.RepositoryURL }}/compare/{{ .Tag.Previous.Name }}...{{ .Tag.Name }}){{ else }}{{ .Tag.Name }}{{ end }}

> &#128640; Generated at {{ datetime "2006-01-02" .Tag.Date }}

{{ range .Commits -}}
* {{ .Subject }} `{{ .Author.Name }} at {{ .Author.Date.Format "2006-01-02 15:04:05 UTC" }}` 
{{ end }}

{{ end -}}
