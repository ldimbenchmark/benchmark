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
  default = "Standard_DS1_v2" # Normal
  # default     = "Standard_DS11-1_v2" # Much memory
  description = "The VM Size"
}

variable "benchmark_complexity_word" {
  type = string
  validation {
    condition     = contains(["days", "junctions"], var.benchmark_complexity_word)
    error_message = "benchmark_complexity_word must be either 'days' or 'junctions'"
  }
  default     = "days"
  description = "type of benchmark"
}

variable "benchmark_normal_word" {
  type = string
  validation {
    condition     = contains(["grid", "single", "sensitivity"], var.benchmark_normal_word)
    error_message = "benchmark_normal_word must be either 'grid' or 'single', 'sensitivity'"
  }
  default     = "grid"
  description = "type of benchmark"
}

variable "benchmark_type" {
  type = string
  validation {
    condition     = contains(["complexity", "normal"], var.benchmark_type)
    error_message = "benchmark_type must be either 'complexity' or 'normal'"
  }
  default     = "normal"
  description = "type of benchmark"
}
