// Muestra datos útiles al final (como IP pública).

output "resource_group_name" {
  description = "Nombre del Resource Group creado"
  value       = azurerm_resource_group.main.name
}

output "public_ip_address" {
  description = "Dirección IP pública de la VM"
  value       = azurerm_public_ip.main.ip_address
}

output "random_name_generated" {
  description = "Nombre aleatorio generado por random_pet"
  value       = random_pet.resource_group.id  # Ejemplo: "rg-happy-panda"
}

