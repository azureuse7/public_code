variable "kubeconfig_path" {
  description = "Path to the kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "kubeconfig_context" {
  description = "Kubeconfig context to use (leave empty to use current context)"
  type        = string
  default     = ""
}

variable "falco_namespace" {
  description = "Kubernetes namespace for Falco"
  type        = string
  default     = "falco"
}

variable "falco_chart_version" {
  description = "Falco Helm chart version"
  type        = string
  default     = "4.3.0"
}
