// Variables opcionales.

variable "location" {
  type    = string
  default = "westeurope"
}
variable "username" {
  type    = string
  default = "azureuser"
}
variable "ssh_key" {
  type      = string
  default = "~/.ssh/id_rsa.pub"
}
