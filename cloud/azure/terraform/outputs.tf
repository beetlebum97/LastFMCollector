output "resource_group_name" {
  description = "Nombre del Resource Group creado"
  value       = azurerm_resource_group.main.name
}
output "public_ip_address" {
  description = "Dirección IP pública de la VM"
  value       = azurerm_public_ip.main.ip_address
}
