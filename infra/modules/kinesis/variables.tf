variable "stream_name" {
  description = "Name of the Kinesis stream"
  type        = string
}

variable "shard_count" {
  description = "Number of shards for the stream"
  type        = number
  default     = 1
}

variable "retention_period" {
  description = "Data retention period in hours"
  type        = number
  default     = 24
}

variable "shard_level_metrics" {
  description = "List of shard-level metrics to enable"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tag value for CreatedBy tag"
  type        = string
}
