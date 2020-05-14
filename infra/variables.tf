variable "aws_region" {
  description = "The region for the application environment - Default is Frankfurt as our main region"
  default     = "eu-central-1"
}

variable "tags" {
  description = "Common tags shared across all resources, specific tags are in the resources"
  type = object({
    Application = string,
    Component   = string
  })
  default = {
    Application = "poe-item-alerts"
    Component   = "poe-item-search-bot"
  }
}

