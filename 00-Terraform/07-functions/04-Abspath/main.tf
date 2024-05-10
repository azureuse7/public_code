locals {
  # Get an absolute path of the spokes from the local repo
  spoke_allow_list_src_path = abspath("${path.root}/../../org/spoke")
}

output sana {
  value       = local.spoke_allow_list_src_path

}

# Changes to Outputs:
#   + sana = "/Users/Gautam.Thakur/Documents/org/spoke"