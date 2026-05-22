{{- define "server-chart.name" -}}
{{- .Chart.Name }}
{{- end }}

{{- define "server-chart.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "server-chart.labels" -}}
app.kubernetes.io/name: {{ include "server-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "server-chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "server-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
