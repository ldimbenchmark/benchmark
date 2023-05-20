variable "resource_group_location" {
  type        = string
  default     = "eastus"
  description = "Location of the resource group."
}

variable "storage_account_name" {
  type        = string
  default     = "masterthesisdata"
  description = "Name of the Storage account used for 'caching'"
}

variable "vm_size" {
  type = string
  # default     = "Standard_D2s_v3" # Double
  default     = "Standard_DS1_v2" # Normal
  # default     = "Standard_DS11-1_v2" # Much memory
  description = "The VM Size"
}
